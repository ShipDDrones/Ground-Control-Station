import asyncio

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

    async def connect(self):
        self.output = "Connecting.."
        try:
            # await asyncio.wait_for(self.drone.connect(system_address="udp://:14540"), timeout=5)
            await asyncio.wait_for(self.drone.connect(system_address="serial:///COM3:57600"), timeout=5)
            self.output = "Connected"
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

    # async def goNorth(self, newLat, newLon):
    #     if not self.airborne:
    #         self.output = "Drone is not armed"
    #         return
    #     try:
    #         async for terrain_info in self.drone.telemetry.home():
    #             absolute_altitude = terrain_info.absolute_altitude_m
    #             break
    #         await self.drone.action.goto_location(newLat, newLon, absolute_altitude, 0)

    async def launch(self, destination):

        mission_items = []
        # mission_items.append(MissionItem(47.398039859999997,
        #                                  8.5455725400000002,
        #                                  25,
        #                                  10,
        #                                  True,
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  MissionItem.CameraAction.NONE,
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan')))
        mission_items.append(MissionItem(destination[0],
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
                                         float('nan')))
        # mission_items.append(MissionItem(47.397825620791885,
        #                                  8.5450092830163271,
        #                                  25,
        #                                  10,
        #                                  True,
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  MissionItem.CameraAction.NONE,
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan'),
        #                                  float('nan')))

        mission_plan = MissionPlan(mission_items)

        try:
            await self.drone.mission.set_return_to_launch_after_mission(False)
        except RuntimeError as re:
            self.output = "Failure - not connected to drone"
            return

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

        running_tasks = [mission_progress_task]
        termination_task = asyncio.ensure_future(
            self.observe_is_in_air(running_tasks))

        await termination_task
        self.onMission = False
        self.airborne = False
        self.armed = False
        self.output = "Mission finished"

    async def mission_progress(self):
        async for mission_progress in self.drone.mission.mission_progress():
            self.output = "Mission progress: " + str(mission_progress.current) + "/" + str(mission_progress.total)
            if not self.airborne:
                return
            if mission_progress.current == mission_progress.total:
                await self.drone.action.land()
                return

    async def observe_is_in_air(self, running_tasks):

        was_in_air = False

        async for is_in_air in self.drone.telemetry.in_air():

            if is_in_air:
                was_in_air = is_in_air

            if was_in_air and not is_in_air:
                for task in running_tasks:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                await asyncio.get_event_loop().shutdown_asyncgens()

                return
