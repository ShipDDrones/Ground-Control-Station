from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy_garden.mapview import MapView, MapMarker
from kivymd.uix.screen import Screen


class Background(Screen):

    def __init__(self, **kwargs):
        super(Background, self).__init__(**kwargs)

        Window.bind(on_resize=self.on_window_resize)

        with self.canvas.before:
            Rectangle(source='images/background2.jpg', pos=self.pos, size=Window.size)

    def on_window_resize(self, window, width, height):
        with self.canvas.before:
            Rectangle(source='images/background2.jpg', pos=self.pos, size=window.size)


class ShipD(App):
    Window.size = (1400, 700)

    def __init__(self, **kwargs):
        super().__init__()
        Window.bind(on_request_close=self.onClose)
        self.running = True
        self.launchButton = None
        self.takeoffButton = None
        self.landButton = None
        self.batteryLeft = None
        self.armButton = None
        self.disarmButton = None
        self.connectButton = None
        self.arrivalTime = None
        self.distance = None
        self.endLabel = None
        self.wind = None
        self.weather = None
        self.destination = None
        self.liveBattery = None
        self.altitude = None
        self.speed = None
        self.timeLeft = None
        self.attachedImage = None
        self.map = None
        self.isDroneSet = None
        self.markerStart = None
        self.markerEnd = None
        self.errorLabel = Label(text="All is well", font_size='25sp', markup=True,
                                size_hint=(1, 0.2))
        self.droneStartButton = Button(text="[font=Bahnschrift]Get drone location[/font]",
                                       size_hint=(.1, .1),
                                       markup=True)
        self.destinationButton = Button(text="[font=Bahnschrift]Set drone destination[/font]",
                                        size_hint=(.1, .1),
                                        markup=True)
        self.connectButton = Button(text="[font=Bahnschrift]Establish connection[/font]", markup=True)
        self.armButton = Button(text="[font=Bahnschrift]Arm[/font]", markup=True)
        self.disarmButton = Button(text="[font=Bahnschrift]Disarm[/font]", markup=True)
        self.takeoffButton = Button(text="[font=Bahnschrift]Takeoff[/font]", markup=True)
        self.landButton = Button(text="[font=Bahnschrift]Land[/font]", markup=True)
        self.launchButton = Button(text="[font=Bahnschrift]Launch mission[/font]", markup=True)
        self.checkButton = Button(text="[font=Bahnschrift]Check package[/font]", markup=True, font_size=20,
                                  size_hint=(1, 0.07))

    def onClose(self, _):
        self.running = False

    def build(self):
        screen = Background()

        both = BoxLayout(orientation='horizontal', spacing=60, padding=30)

        leftSide = BoxLayout(orientation='vertical', spacing=20, pos=(0, 0), size_hint=(0.6, 1))

        self.map = MapView(zoom=13, size_hint=(1, 1))

        self.map.center_on(46.769379, 23.5899542)

        self.markerStart = MapMarker()
        self.markerEnd = MapMarker()
        self.map.add_widget(self.markerStart)
        self.map.add_widget(self.markerEnd)

        locations = GridLayout(cols=2, size_hint=(1, .18), spacing=13, pos=(10, 0))

        self.destination = TextInput(font_size=20,
                                     size_hint=(.2, .1))

        self.isDroneSet = Label(text="[font=Bahnschrift]Missing drone position[/font]", size_hint=(.2, .1),
                                font_size='15sp', markup=True)

        locations.add_widget(self.isDroneSet)
        locations.add_widget(self.droneStartButton)
        locations.add_widget(self.destination)
        locations.add_widget(self.destinationButton)

        leftSide.add_widget(self.map)
        leftSide.add_widget(locations)

        rightSide = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=10)

        infoLabel = Label(text="[font=Bahnschrift]Mission information[/font]", font_size='25sp', markup=True,
                          size_hint=(1, 0.1))

        missionInfo = GridLayout(cols=2, spacing=10, size_hint=(1, 0.4))

        self.endLabel = Label(text="[font=Bahnschrift]No destination set[/font]", font_size='15sp', markup=True)

        self.weather = Label(text="[font=Bahnschrift]Weather[/font]", font_size='15sp', markup=True)

        self.wind = Label(text="[font=Bahnschrift]Wind speed[/font]", font_size='15sp', markup=True)

        self.arrivalTime = Label(text="[font=Bahnschrift]Arrival time[/font]", font_size='15sp', markup=True)

        self.distance = Label(text="[font=Bahnschrift]Distance to destination[/font]", font_size='15sp', markup=True)

        self.batteryLeft = Label(text="[font=Bahnschrift]Battery left on arrival[/font]", font_size='15sp', markup=True)

        controlLabel = Label(text="[font=Bahnschrift]Drone control[/font]", font_size='25sp', markup=True,
                             size_hint=(1, 0.1))

        droneControl = GridLayout(cols=2, spacing=20, size_hint=(1, 0.3))

        missionInfo.add_widget(self.endLabel)
        missionInfo.add_widget(self.arrivalTime)
        missionInfo.add_widget(self.weather)
        missionInfo.add_widget(self.wind)
        missionInfo.add_widget(self.batteryLeft)
        missionInfo.add_widget(self.distance)

        droneControl.add_widget(self.connectButton)
        droneControl.add_widget(self.armButton)
        droneControl.add_widget(self.disarmButton)
        droneControl.add_widget(self.takeoffButton)
        droneControl.add_widget(self.landButton)
        droneControl.add_widget(self.launchButton)

        rightSide.add_widget(infoLabel)
        rightSide.add_widget(missionInfo)
        rightSide.add_widget(controlLabel)
        rightSide.add_widget(droneControl)
        rightSide.add_widget(self.errorLabel)

        moreRightSide = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=10)

        flightLabel = Label(text="[font=Bahnschrift]Flight information[/font]", font_size='25sp', markup=True,
                            size_hint=(1, 0.1))

        self.liveBattery = Label(text="[font=Bahnschrift]Current battery - [/font]", font_size='20sp', markup=True,
                                 size_hint=(1, 0.1))

        self.altitude = Label(text="[font=Bahnschrift]Current altitude - [/font]", font_size='20sp', markup=True,
                              size_hint=(1, 0.1))

        self.speed = Label(text="[font=Bahnschrift]Current ground speed - [/font]", font_size='20sp', markup=True,
                           size_hint=(1, 0.1))

        self.timeLeft = Label(text="[font=Bahnschrift]Time until arrival - [/font]", font_size='20sp', markup=True,
                              size_hint=(1, 0.1))

        self.attachedImage = Image(size_hint=(1, 0.3))

        moreRightSide.add_widget(flightLabel)
        moreRightSide.add_widget(self.liveBattery)
        moreRightSide.add_widget(self.altitude)
        moreRightSide.add_widget(self.speed)
        moreRightSide.add_widget(self.timeLeft)
        moreRightSide.add_widget(self.attachedImage)
        moreRightSide.add_widget(self.checkButton)

        both.add_widget(leftSide)
        both.add_widget(rightSide)
        both.add_widget(moreRightSide)

        screen.add_widget(both)

        return screen
