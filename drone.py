import asyncio
import math

from mavsdk import System
from mavsdk.action import *
from mavsdk.mission import (MissionItem, MissionPlan)


class Drone:

    def __init__(self):
        self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.output = "All is well"
        self.airborne = False
        self.armed = False
        self.onMission = False
        self.battery = 100
        self.speed = 0
        self.altitude = 0
        self.connected = False
        self.position = (None, None)

    async def connect(self):
        self.output = "Connecting.."
        try:
            # await asyncio.wait_for(self.drone.connect(system_address="udp://:14540"), timeout=5)
            await asyncio.wait_for(self.drone.connect(system_address="serial:///COM8:57600"), timeout=5)
            self.output = "Connected"
            self.connected = True
        except asyncio.TimeoutError:
            self.output = "Failed to connect"

    async def arm(self):
        if self.airborne:
            self.output = "Drone is already in flight"
            return
        if self.armed:
            self.output = "Drone is already armed"
            return
        try:
            await self.drone.action.arm()
            self.armed = True
            self.output = "Armed"
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"
        except ActionError as ae:
            self.output = "Failure - GPS not connected"

    async def disarm(self):
        if not self.armed:
            self.output = "Drone is already disarmed"
            return
        try:
            await self.drone.action.disarm()
            self.output = "Disarmed"
            self.armed = False
        except ActionError as ae:
            self.output = "Failure - drone has not yet landed"
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"

    async def takeOff(self):
        if self.airborne:
            self.output = "Drone is already in flight"
            return
        if not self.armed:
            self.output = "Drone is not armed"
            return
        try:
            await self.drone.action.takeoff()
            self.airborne = True
            self.output = "Taking off"
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"
        except ActionError as ae:
            self.output = "Failure - GPS not connected"

    async def land(self):
        if not self.airborne:
            self.output = "Drone is already on the ground"
            return
        try:
            await self.drone.action.land()
            self.airborne = False
            self.output = "Landed"
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"

    async def launch(self, destination):

        try:
            await self.drone.mission.set_return_to_launch_after_mission(False)
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"
            return

        if destination[0] is None or destination[1] is None:
            self.output = "Failure - start and destination not clear"
            return

        mission_items = [MissionItem(destination[0],
                                     destination[1],
                                     25,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'))]

        mission_plan = MissionPlan(mission_items)

        await self.drone.mission.upload_mission(mission_plan)

        self.output = "Waiting a for global position estimate..."
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                break

        await self.drone.action.arm()
        self.armed = True

        await self.drone.mission.start_mission()
        self.output = "Mission started"
        self.onMission = True
        self.airborne = True

        mission_progress_task = asyncio.ensure_future(
            self.mission_progress())
        drone_position_task = asyncio.ensure_future(
            self.update_drone_position())
        drone_battery_task = asyncio.ensure_future(
            self.update_drone_battery())
        drone_speed_task = asyncio.ensure_future(
            self.update_drone_speed())

        running_tasks = [mission_progress_task, drone_position_task, drone_battery_task, drone_speed_task]
        termination_task = asyncio.ensure_future(
            self.observe_is_in_air(running_tasks))

        await termination_task
        self.onMission = False
        self.armed = False
        self.output = "Mission finished"

    async def mission_progress(self):
        async for mission_progress in self.drone.mission.mission_progress():
            self.output = "Mission progress: " + str(mission_progress.current) + "/" + str(mission_progress.total)
            if mission_progress.current == mission_progress.total:
                await self.drone.action.land()
                self.airborne = False
                return

    async def get_start_position(self):
        if not self.connected:
            self.output = "Not connected to drone"
            return

        async for position in self.drone.telemetry.position():
            self.position = (position.latitude_deg, position.longitude_deg)
            return

    async def update_drone_speed(self):
        async for data in self.drone.telemetry.velocity_ned():
            self.speed = round(math.sqrt(data.east_m_s * data.east_m_s + data.north_m_s * data.north_m_s) * 3.6, 2)

    async def update_drone_battery(self):
        async for battery in self.drone.telemetry.battery():
            self.battery = round(battery.remaining_percent * 100, 1)

    async def update_drone_position(self):
        async for position in self.drone.telemetry.position():
            self.position = (position.latitude_deg, position.longitude_deg)
            self.altitude = round(position.relative_altitude_m, 3)

    async def observe_is_in_air(self, running_tasks):

        was_in_air = False

        async for is_in_air in self.drone.telemetry.in_air():

            if is_in_air:
                was_in_air = is_in_air

            if was_in_air and not is_in_air:
                for task in running_tasks:
                    if not self.airborne:
                        task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                await asyncio.get_event_loop().shutdown_asyncgens()

                return
