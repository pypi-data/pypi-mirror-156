# AVR-Python-Libraries

## Install

To install the base package, run:

```bash
pip install bell-avr-libraries
```

Additionally, the `mqtt` and `serial` extras are available if you want to use
the MQTT or PCC functionality.

```bash
pip install bell-avr-libraries[mqtt,serial]
```

## Usage

### MQTT

```python
from bell.avr import mqtt
```

These are MQTT utilities that are used to have a consistent messaging protocol
throughout all the AVR software modules.

The first part of this are the payloads for the MQTT messages themselves. As AVR
exclusively uses JSON, these are all
[`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict)s
that have all of the required fields for a message.

Example:

```python
from bell.avr.mqtt.payloads import AvrPcmSetBaseColorPayload

payload = AvrPcmSetBaseColorPayload((128, 232, 142, 0))
```

The second part of the MQTT libraries, is the `MQTTModule` class.
This is a boilerplate module for AVR that makes it very easy to send
and recieve MQTT messages and do something with them.

Example:

```python
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrFcmVelocityPayload, AvrPcmSetServoOpenClosePayload


class Sandbox(MQTTModule):
    def __init__(self) -> None:
        self.topic_map = {"avr/fcm/velocity": self.show_velocity}

    def show_velocity(self, payload: AvrFcmVelocityPayload) -> None:
        vx = payload["vX"]
        vy = payload["vY"]
        vz = payload["vZ"]
        v_ms = (vx, vy, vz)
        print(f"Velocity information: {v_ms} m/s")

    def open_servo(self) -> None:
        payload = AvrPcmSetServoOpenClosePayload(servo=0, action="open")
        self.send_message("avr/pcm/set_servo_open_close", payload)


if __name__ == "__main__":
    box = Sandbox()
    box.run()
```

The `topic_map` dictionary is a class attribute that maps topics to subscribe to
and a function that will handle an incoming payload. The `payload` argument
should match the appropriate `Payload` class for that topic.

Additionally, the `message_cache` attribute is a dictionary that holds
a copy of the last payload sent by that module on a given topic. The keys are the
topic strings, and the values are the topic payloads.

### Utils

```python
from bell.avr import utils
```

These are general purpose utilities.

#### Decorators

```python
from bell.avr.utils import decorators
```

There are 3 different function decorators available, which are helpful for MQTT
message callbacks. First is the `try_except` decorator, which wraps the
function in a `try: except:` statement and will log any exceptions to the console:

```python
    @decorators.try_except
    def assemble_hil_gps_message(self) -> None:
        ...
```

Additionally, there is the `reraise` argument, which can be set to `True` to raise
any exceptions that are encountered. This is helpful if you still want exceptions
to propagate up, but log them.

There is an async version of this decorator as well with an `async_` prefix.

```python
    @decorators.async_try_except()
    async def connected_status_telemetry(self) -> None:
        ...
```

The last decorator is `run_forever` which will run the wrapped function forever,
with a given `period` or `frequency`.

```python
    @decorators.run_forever(frequency=5)
    def read_data(self) -> None:
        ...
```

#### Timing

```python
from bell.avr.utils import timing
```

Here is a `rate_limit` function which take a callable and a
period or frequency, and only run the callable at that given rate.

```python
for _ in range(10):
    # add() will only run twice
    timing.rate_limit(add, period=5)
    time.sleep(1)
```

This works tracking calls to the `rate_limit` function from a line number
within a file, so multiple calls to `rate_limit` say within a loop
with the same callable and period will be treated seperately. This allows
for dynamic frequency manipulation.

### Serial

```python
from bell.avr import serial
```

These are serial utilities that help facilitate finding and communicating
with the AVR peripherial control computer.

#### Client

```python
from bell.avr.serial import client
```

The `SerialLoop` class is a small wrapper around the `pyserial` `serial.Serial`
class which adds a `run` method that will try to read data from the serial device
as fast as possible.

```python
ser = client.SerialLoop()
```

#### PCC

```python
from bell.avr.serial import client
```

The `PeripheralControlComputer` class sends serial messages
to the AVR peripherial control computer, via easy-to-use class methods.

```python
import bell.avr.serial
import threading

client = bell.avr.serial.client.SerialLoop()
client.port = port
client.baudrate = baudrate

pcc = bell.avr.serial.pcc.PeripheralControlComputer(client)

client_thread = threading.Thread(target=client.run)
client_thread.start()

pcc.set_servo_max(0, 100)
```

#### Ports

```python
from bell.avr.serial import ports
```

Here is a `list_serial_ports` function which returns a list of detected serial
ports connected to the system.

```python
serial_ports = ports.list_serial_ports()
# ["COM1", "COM5", ...]
```

## Development

Install [`poetry`](https://python-poetry.org/) and run
`poetry install --extras mqtt --extras serial` to install of the dependencies
inside a virtual environment.

Build the auto-generated code with `poetry run python build.py`. From here,
you can now produce a package with `poetry build`.

To add new message definitions, add entries to the `bell/avr/mqtt/messages.jsonc` file.
The 3 parts of a new message are as follows:

1. "topic": This is the full topic path for the message. This must be all lower case and
   start with "avr/".
2. "payload": These are the keys of the payload for the message.
   This is a list of key entries (see below).
3. "docs": This is an optional list of Markdown strings that explains what this
   message does. Each list item is a new line.

The key entries for a message have the following elements:

1. "key": This is the name of the key. Must be a valid Python variable name.
2. "type": This is the data type of the key such as `Tuple[int, int, int, int]`.
   Must be a valid Python type hint. Otherwise, this can be a list of more
   key entries, effectively creating a nested dictionary.
3. "docs": This is an optional list of Markdown strings that explains what the
   key is. Each list item is a new line.

The `bell/avr/mqtt/schema.json` file will help ensure the correct schema is maintained,
assuming you are using VS Code.

## MQTT Documentation

### Data Types

#### AvrApriltagsSelectedPos

The position of the vehicle in world frame **in cm**

- `"n"` (`float`): The +north position of the vehicle relative to the world origin in world frame
- `"e"` (`float`): The +east position of the vehicle relative to the world origin in world frame
- `"d"` (`float`): The +down position of the vehicle relative to the world origin in world frame

#### AvrApriltagsRawTags

- `"id"` (`int`): The ID of the tag
- `"pos"` (`AvrApriltagsRawTagsPos`)
- `"rotation"` (`Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]`): The 3x3 rotation matrix

#### AvrApriltagsRawTagsPos

- `"x"` (`float`): The position **in meters** of the camera relative to the **tag's x** frame
- `"y"` (`float`): The position **in meters** of the camera relative to the **tag's y** frame
- `"z"` (`float`): The position **in meters** of the camera relative to the **tag's z** frame

#### AvrApriltagsVisibleTags

- `"id"` (`int`): The ID of the tag
- `"horizontal_dist"` (`float`): The horizontal scalar distance from vehicle to tag, **in cm**
- `"vertical_dist"` (`float`): The vertical scalar distance from vehicle to tag, **in cm**
- `"angle_to_tag"` (`float`): The angle formed by the vector pointing from the vehicles body to the tag in world frame relative to world-north
- `"heading"` (`float`): The heading of the vehicle in world frame
- `"pos_rel"` (`AvrApriltagsVisibleTagsPosRel`): The relative position of the vehicle to the tag in world frame **in cm**
- `"pos_world"` (`AvrApriltagsVisibleTagsPosWorld`): The position of the vehicle in world frame **in cm** (if the tag has no truth data, this will not be present in the output)

#### AvrApriltagsVisibleTagsPosRel

The relative position of the vehicle to the tag in world frame **in cm**

- `"x"` (`float`): The x (+north/-south) position of the vehicle relative to the tag in world frame (for reference the mountain is **north** of the beach)
- `"y"` (`float`): The y (+east/-west) position of the vehicle relative to the tag in world frame
- `"z"` (`float`): The z (+down/-up) position of the vehicle relative to the tag in world frame (no, this is not a typo, up is really - )

#### AvrApriltagsVisibleTagsPosWorld

The position of the vehicle in world frame **in cm** (if the tag has no truth data, this will not be present in the output)

- `"x"` (`Optional[float]`): The x position of the vehicle relative to the world origin (this is the ship) in world frame (for reference the mountain is **north** of the beach)
- `"y"` (`Optional[float]`): The y position of the vehicle relative to the world origin in world frame
- `"z"` (`Optional[float]`): The z position of the vehicle relative to the world origin in world frame

### Message Payloads

#### AvrAutonomousPayload

Topic: `avr/autonomous`

This enables enable or disable autonomous mode. This is not used by any Bell code, but available to students to listen to who may wish to not always be running their autonomous mode,

- `"enable"` (`bool`)

#### AvrPcmSetBaseColorPayload

Topic: `avr/pcm/set_base_color`

This sets the color of the LED strip on the PCC

- `"wrgb"` (`Tuple[int, int, int, int]`): A list of 4 `int`s between 0 and 255 to set the base color of the LEDs. Example: [255, 0, 128, 255].

#### AvrPcmSetTempColorPayload

Topic: `avr/pcm/set_temp_color`

This sets the color of the LED strip on the PCC temporarily

- `"wrgb"` (`Tuple[int, int, int, int]`): A list of 4 `int`s between 0 and 255 to set the base color of the LEDs. Example: [255, 0, 128, 255].
- `"time"` (`float`): Optional `float` for the number of seconds the color should be set for. Default is 0.5.

#### AvrPcmSetLaserOnPayload

Topic: `avr/pcm/set_laser_on`

There is no content for this class

#### AvrPcmSetLaserOffPayload

Topic: `avr/pcm/set_laser_off`

There is no content for this class

#### AvrPcmSetServoOpenClosePayload

Topic: `avr/pcm/set_servo_open_close`

- `"servo"` (`int`): ID of the servo to open or close as an `int`. This is 0-indexed.
- `"action"` (`Literal["open", "close"]`): Either the literal string "open" or "close".

#### AvrPcmSetServoMinPayload

Topic: `avr/pcm/set_servo_min`

- `"servo"` (`int`): ID of the servo to set the minimum pulse width as an `int`. This is 0-indexed.
- `"min_pulse"` (`int`): A `int` between 0 and 1000.

#### AvrPcmSetServoMaxPayload

Topic: `avr/pcm/set_servo_max`

- `"servo"` (`int`): ID of the servo to set the maximum pulse width as an `int`. This is 0-indexed.
- `"max_pulse"` (`int`): A `int` between 0 and 1000.

#### AvrPcmSetServoPctPayload

Topic: `avr/pcm/set_servo_pct`

- `"servo"` (`int`): ID of the servo to set the percent as an `int`. This is 0-indexed.
- `"percent"` (`int`): A `int` between 0 and 100.

#### AvrPcmResetPayload

Topic: `avr/pcm/reset`

This resets the PCC

There is no content for this class

#### AvrFcmHilGpsStatsPayload

Topic: `avr/fcm/hil_gps_stats`

- `"num_frames"` (`int`)

#### AvrFcmEventsPayload

Topic: `avr/fcm/events`

- `"name"` (`str`)
- `"payload"` (`str`)
- `"timestamp"` (`str`)

#### AvrFcmBatteryPayload

Topic: `avr/fcm/battery`

- `"voltage"` (`float`): Battery voltage
- `"soc"` (`float`): State of charge (0 - 100)
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmStatusPayload

Topic: `avr/fcm/status`

- `"armed"` (`bool`): True/False if the drone is currently armed
- `"mode"` (`str`): Current flight mode, which is one of the following:
    - 'UNKNOWN'
    - 'READY'
    - 'TAKEOFF'
    - 'HOLD'
    - 'MISSION'
    - 'RETURN_TO_LAUNCH'
    - 'LAND'
    - 'OFFBOARD'
    - 'FOLLOW_ME'
    - 'MANUAL'
    - 'ALTCTL'
    - 'POSCTL'
    - 'ACRO'
    - 'STABILIZED'
    - 'RATTITUDE'
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmLocationLocalPayload

Topic: `avr/fcm/location/local`

- `"dX"` (`float`): X position in a local North/East/Down coordinate system
- `"dY"` (`float`): Y position in a local North/East/Down coordinate system
- `"dZ"` (`float`): Z position in a local North/East/Down coordinate system
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmLocationGlobalPayload

Topic: `avr/fcm/location/global`

- `"lat"` (`float`): Latitude in global coordinates
- `"lon"` (`float`): Longitude in global coordinates
- `"alt"` (`float`): Relative altitude in global coordinates
- `"hdg"` (`float`): Heading
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmLocationHomePayload

Topic: `avr/fcm/location/home`

- `"lat"` (`float`): Latitude relative to the home position
- `"lon"` (`float`): Longitude relative to the home position
- `"alt"` (`float`): Relative altitude to the home position
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmAttitudeEulerPayload

Topic: `avr/fcm/attitude/euler`

- `"roll"` (`float`): Roll in degrees
- `"pitch"` (`float`): Pitch in degrees
- `"yaw"` (`float`): Yaw in degrees
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmVelocityPayload

Topic: `avr/fcm/velocity`

- `"vX"` (`float`): X velocity in a local North/East/Down coordinate system
- `"vY"` (`float`): Y velocity in a local North/East/Down coordinate system
- `"vZ"` (`float`): Z velocity in a local North/East/Down coordinate system
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFcmGpsInfoPayload

Topic: `avr/fcm/gps_info`

- `"num_satellites"` (`int`): Number of visible satellites in use
- `"fix_type"` (`str`): GPS fix type
- `"timestamp"` (`str`): Time the message was sent in [ISO 8601 format](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)

#### AvrFusionPositionNedPayload

Topic: `avr/fusion/position/ned`

- `"n"` (`float`)
- `"e"` (`float`)
- `"d"` (`float`)

#### AvrFusionVelocityNedPayload

Topic: `avr/fusion/velocity/ned`

- `"Vn"` (`float`)
- `"Ve"` (`float`)
- `"Vd"` (`float`)

#### AvrFusionGeoPayload

Topic: `avr/fusion/geo`

- `"lat"` (`float`)
- `"lon"` (`float`)
- `"alt"` (`float`)

#### AvrFusionGroundspeedPayload

Topic: `avr/fusion/groundspeed`

- `"groundspeed"` (`float`)

#### AvrFusionCoursePayload

Topic: `avr/fusion/course`

- `"course"` (`float`)

#### AvrFusionClimbratePayload

Topic: `avr/fusion/climbrate`

- `"climb_rate_fps"` (`float`)

#### AvrFusionAttitudeQuatPayload

Topic: `avr/fusion/attitude/quat`

- `"w"` (`float`)
- `"x"` (`float`)
- `"y"` (`float`)
- `"z"` (`float`)

#### AvrFusionAttitudeEulerPayload

Topic: `avr/fusion/attitude/euler`

- `"psi"` (`float`)
- `"theta"` (`float`)
- `"phi"` (`float`)

#### AvrFusionAttitudeHeadingPayload

Topic: `avr/fusion/attitude/heading`

- `"heading"` (`float`)

#### AvrFusionHilGpsPayload

Topic: `avr/fusion/hil_gps`

- `"time_usec"` (`int`)
- `"fix_type"` (`int`)
- `"lat"` (`int`)
- `"lon"` (`int`)
- `"alt"` (`int`)
- `"eph"` (`int`)
- `"epv"` (`int`)
- `"vel"` (`int`)
- `"vn"` (`int`)
- `"ve"` (`int`)
- `"vd"` (`int`)
- `"cog"` (`int`)
- `"satellites_visible"` (`int`)
- `"heading"` (`int`)

#### AvrVioResyncPayload

Topic: `avr/vio/resync`

- `"n"` (`float`)
- `"e"` (`float`)
- `"d"` (`float`)
- `"heading"` (`float`)

#### AvrVioPositionNedPayload

Topic: `avr/vio/position/ned`

- `"n"` (`float`)
- `"e"` (`float`)
- `"d"` (`float`)

#### AvrVioVelocityNedPayload

Topic: `avr/vio/velocity/ned`

- `"n"` (`float`)
- `"e"` (`float`)
- `"d"` (`float`)

#### AvrVioOrientationEulPayload

Topic: `avr/vio/orientation/eul`

- `"psi"` (`float`)
- `"theta"` (`float`)
- `"phi"` (`float`)

#### AvrVioOrientationQuatPayload

Topic: `avr/vio/orientation/quat`

- `"w"` (`float`)
- `"x"` (`float`)
- `"y"` (`float`)
- `"z"` (`float`)

#### AvrVioHeadingPayload

Topic: `avr/vio/heading`

- `"degrees"` (`float`)

#### AvrVioConfidencePayload

Topic: `avr/vio/confidence`

- `"tracker"` (`float`): Number between 0 and 100 of tracking confidence

#### AvrApriltagsSelectedPayload

Topic: `avr/apriltags/selected`

This topic publishes its best candidate for position feedback

- `"tag_id"` (`int`): The id of the tag
- `"pos"` (`AvrApriltagsSelectedPos`): The position of the vehicle in world frame **in cm**
- `"heading"` (`float`)

#### AvrApriltagsRawPayload

Topic: `avr/apriltags/raw`

This topic publishes the raw tag data

- `"tags"` (`List[AvrApriltagsRawTags]`)

#### AvrApriltagsVisiblePayload

Topic: `avr/apriltags/visible`

This topic publishes the transformed tag data

- `"tags"` (`List[AvrApriltagsVisibleTags]`)

#### AvrApriltagsFpsPayload

Topic: `avr/apriltags/fps`

- `"fps"` (`int`)

#### AvrThermalReadingPayload

Topic: `avr/thermal/reading`

- `"data"` (`str`)

#### AvrStatusLightPcmPayload

Topic: `avr/status/light/pcm`

There is no content for this class

#### AvrStatusLightVioPayload

Topic: `avr/status/light/vio`

There is no content for this class

#### AvrStatusLightApriltagsPayload

Topic: `avr/status/light/apriltags`

There is no content for this class

#### AvrStatusLightFcmPayload

Topic: `avr/status/light/fcm`

There is no content for this class

#### AvrStatusLightThermalPayload

Topic: `avr/status/light/thermal`

There is no content for this class
