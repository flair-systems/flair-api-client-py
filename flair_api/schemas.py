from marshmallow_jsonapi import Schema, fields
from .models import Tombstone

def dasherize(text):
    return text.replace('_', '-')

class UserSchema(Schema):
    id = fields.String(load_only=True)
    name = fields.String(validate=validate.Length(min=1))
    email = fields.Email()
    role = fields.String()
    password = fields.String(dump_only=True)
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    editable_structures = fields.Relationship(
        self_url="/api/users/{user_id}/relationships/editable-structures",
        self_url_kwargs={'user_id': '<id>'},
        related_url="/api/users/{user_id}/editable-structures",
        related_url_kwargs={'user_id': '<id>'},
        many=True,
        include_data=True,
        type_="structures"
    )

    viewable_structures = fields.Relationship(
        self_url="/api/users/{user_id}/relationships/viewable-structures",
        self_url_kwargs={'user_id': '<id>'},
        related_url="/api/users/{user_id}/viewable-structures",
        related_url_kwargs={'user_id': '<id>'},
        many=True,
        include_data=True,
        type_="structures"
    )

    adminable_structures = fields.Relationship(
        self_url="/api/users/{user_id}/relationships/adminable-structures",
        self_url_kwargs={'user_id': '<id>'},
        related_url="/api/users/{user_id}/adminable-structures",
        related_url_kwargs={'user_id': '<id>'},
        many=True,
        include_data=True,
        type_="structures"
    )

    default_structure = fields.Relationship(
        self_url="/api/users/{user_id}/relationships/default-structure",
        self_url_kwargs={'user_id': '<id>'},
        related_url="/api/users/{user_id}/default-structure",
        related_url_kwargs={'user_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    devices = fields.Relationship(
        related_url="/api/users/{user_id}/devices",
        related_url_kwargs={'user_id': '<id>'},
        many=True,
        include_data=True,
        type_="devices"
    )

    class Meta:
        type_ = 'users'
        inflect = dasherize

class StructureSchema(Schema):
    id = fields.String(load_only=True)
    name = fields.String()
    structure_type = fields.Integer()
    mode = fields.Integer()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)
    location = fields.String()
    location_type = fields.String()
    puck_client_id = fields.String(load_only=True)
    puck_client_secret = fields.String(load_only=True)
    setup_mode = fields.Boolean()
    city = fields.String()
    state = fields.String()
    zip_code = fields.String()

    class Meta:
        type_ = 'structures'
        inflect = dasherize

    editor_users = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/editor-users",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/editor-users",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="users"
    )

    viewer_users = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/viewer-users",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/viewer-users",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="users"
    )

    admin_users = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/admin-users",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/admin-users",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="users"
    )

    rooms = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/rooms",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/rooms",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="rooms"
    )

    zones = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/zones",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/zones",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="zones"
    )

    hvac_units = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/hvac-units",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/hvac-units",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="hvac-units"
    )

    thermostats = fields.Relationship(
        self_url="/api/structures/{structure_id}/relationships/thermostats",
        self_url_kwargs={'structure_id': '<id>'},
        related_url="/api/structures/{structure_id}/thermostats",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="thermostats"
    )

    weather_readings = fields.Relationship(
        related_url="/api/structures/{structure_id}/weather-readings",
        related_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="weather-readings"
    )

    pucks = fields.Relationship(
        related_url="/api/structures/{structure_id}/pucks",
        related_url_kwargs={'structure_id': '<id>'},
        self_url="/api/structures/{structure_id}/relationships/pucks",
        self_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="pucks"
    )

    vents = fields.Relationship(
        related_url="/api/structures/{structure_id}/vents",
        related_url_kwargs={'structure_id': '<id>'},
        self_url="/api/structures/{structure_id}/relationships/vents",
        self_url_kwargs={'structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="vents"
    )

class OAuthApplicationSchema(Schema):
    id = fields.String(load_only=True)
    name = fields.String()
    description = fields.String()
    client_id = fields.String(load_only=True)
    client_secret = fields.String(load_only=True)
    is_confidential = fields.Bool()
    redirect_uris = fields.List(fields.String())
    default_scopes = fields.List(fields.String())
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    class Meta:
        type_ = 'oauth-applications'
        inflect = dasherize

    user = fields.Relationship(
        related_url="/api/applications/{application_id}/user",
        related_url_kwargs={'application_id': '<id>'},
        self_url="/api/applications/{application_id}/relationships/user",
        self_url_kwargs={'application_id': '<id>'},
        many=False,
        include_data=True,
        type_="users"
    )

class CallbackSchema(Schema):
    id = fields.String(load_only=True)
    web_hook_url = fields.String()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    class Meta:
        type_ = 'callbacks'
        inflect = dasherize

    application = fields.Relationship(
        related_url="/api/callbacks/{callback_id}/application",
        related_url_kwargs={'callback_id': '<id>'},
        many=False,
        include_data=True,
        type_="oauth-applications"
    )

class ZoneSchema(Schema):
    id = fields.String(load_only=True)
    name = fields.String()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    class Meta:
        type_ = 'zones'
        inflect = dasherize

    structure = fields.Relationship(
        related_url="/api/zones/{zone_id}/structure",
        related_url_kwargs={'zone_id': '<id>'},
        self_url="/api/zones/{zone_id}/relationships/structure",
        self_url_kwargs={'zone_id': '<id>'},
        many=False,
        include_data=True,
        type_="users"
    )

    rooms = fields.Relationship(
        related_url="/api/zones/{zone_id}/roomes",
        related_url_kwargs={'zone_id': '<id>'},
        self_url="/api/zones/{zone_id}/relationships/rooms",
        self_url_kwargs={'zone_id': '<id>'},
        many=True,
        include_data=True,
        type_="users"
    )

    thermostat = fields.Relationship(
        related_url="/api/zones/{zone_id}/thermostat",
        related_url_kwargs={'zone_id': '<id>'},
        self_url="/api/zones/{zone_id}/relationships/thermostat",
        self_url_kwargs={'zone_id': '<id>'},
        many=False,
        include_data=True,
        type_="users"
    )

    class Meta:
        type_ = 'zones'
        inflect = dasherize

class WindowSchema(Schema):
    id = fields.UUID()
    direction = fields.String()
    number = fields.Integer()

    class Meta:
        type_ = 'windows'
        inflect = dasherize

class RoomSchema(Schema):
    id = fields.String(load_only=True)
    name = fields.String()
    level = fields.String()
    air_return = fields.Boolean()
    windows = fields.Nested(WindowSchema, many=True)
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    class Meta:
        type_ = 'rooms'
        inflect = dasherize

    puck_apps = fields.Relationship(
        related_url="/api/rooms/{room_id}/puck-apps",
        related_url_kwargs={'room_id': '<id>'},
        self_url="/api/rooms/{room_id}/relationships/puck-apps",
        self_url_kwargs={'room_id': '<id>'},
        many=True,
        include_data=True,
        type_="puck-apps"
    )

    structure = fields.Relationship(
        related_url="/api/rooms/{room_id}/structure",
        related_url_kwargs={'room_id': '<id>'},
        self_url="/api/rooms/{room_id}/relationships/structure",
        self_url_kwargs={'room_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    zone = fields.Relationship(
        related_url="/api/rooms/{room_id}/zone",
        related_url_kwargs={'room_id': '<id>'},
        self_url="/api/rooms/{room_id}/relationships/zones",
        self_url_kwargs={'room_id': '<id>'},
        many=False,
        include_data=True,
        type_="zones"
    )

    hvac_units = fields.Relationship(
        self_url="/api/rooms/{room_id}/relationships/hvac-units",
        self_url_kwargs={'room_id': '<id>'},
        related_url="/api/rooms/{room_id}/hvac-units",
        related_url_kwargs={'room_id': '<id>'},
        many=True,
        include_data=True,
        type_="hvac-units"
    )

    pucks = fields.Relationship(
        related_url="/api/rooms/{room_id}/pucks",
        related_url_kwargs={'room_id': '<id>'},
        self_url="/api/rooms/{room_id}/relationships/pucks",
        self_url_kwargs={'room_id': '<id>'},
        many=True,
        include_data=True,
        type_="pucks"
    )

    vents = fields.Relationship(
        related_url="/api/rooms/{room_id}/vents",
        related_url_kwargs={'room_id': '<id>'},
        self_url="/api/rooms/{room_id}/relationships/vents",
        self_url_kwargs={'room_id': '<id>'},
        many=True,
        include_data=True,
        type_="vents"
    )

    class Meta:
        type_ = 'rooms'
        inflect = dasherize

class PuckStateSchema(Schema):
    id = fields.UUID()
    created_at = fields.DateTime(load_only=True)
    desired_temperature = fields.Integer(validate=validates_unsigned16)
    temperature_display_scale = fields.String()
    is_access_point = fields.Boolean()
    puck_display_color = fields.String()
    orientation = fields.String()
    demo_mode = fields.Integer(validate=validates_unsigned16)
    firmware_version = fields.Integer(validate=validates_unsigned16)
    beacon_interval_ms = fields.Integer(validate=validates_unsigned16)
    bluetooth_tx_power_mw = fields.Integer(validate=validates_unsigned16)
    reporting_interval_ms= fields.Integer(validate=validates_unsigned16)
    sub_ghz_radio_tx_power_mw = fields.Integer(validate=validates_unsigned16)
    display_text = fields.String()
    display_image = fields.String()
    display_ttl_ms = fields.Integer(validate=validates_unsigned16)

    puck = fields.Relationship(
        related_url="/api/puck-states/{puck_state_id}/puck",
        related_url_kwargs={'puck_state_id': '<id>'},
        many=False,
        include_data=True,
        type_="pucks"
    )


    class Meta:
        type_ = 'puck-states'
        inflect = dasherize

class PuckSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    display_number = fields.String(load_only=True)
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    current_state = fields.Relationship(
        related_url="/api/pucks/{puck_id}/current-state",
        related_url_kwargs={'puck_id': '<id>'},
        many=False,
        include_data=True,
        type_="puck-states"
    )

    previous_state = fields.Relationship(
        related_url="/api/pucks/{puck_id}/previous-state",
        related_url_kwargs={'puck_id': '<id>'},
        many=False,
        include_data=True,
        type_="puck-states"
    )

    room = fields.Relationship(
        related_url="/api/pucks/{puck_id}/room",
        related_url_kwargs={'puck_id': '<id>'},
        self_url="/api/pucks/{puck_id}/relationships/room",
        self_url_kwargs={'puck_id': '<id>'},
        many=False,
        include_data=True,
        type_="rooms"
    )

    structure = fields.Relationship(
        related_url="/api/pucks/{puck_id}/structure",
        related_url_kwargs={'puck_id': '<id>'},
        self_url="/api/pucks/{puck_id}/relationships/structure",
        self_url_kwargs={'puck_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    beacon_sightings = fields.Relationship(
        related_url="/api/pucks/{puck_id}/beacon-sightings",
        related_url_kwargs={'puck_id': '<id>'},
        many=True,
        include_data=True,
        type_="beacon-sightings"
    )

    sensor_readings = fields.Relationship(
        related_url="/api/pucks/{puck_id}/sensor-readings",
        related_url_kwargs={'puck_id': '<id>'},
        many=True,
        include_data=False,
        type_="sensor-readings"
    )

    class Meta:
        type_ = 'pucks'
        inflect = dasherize

class VentSensorReadingSchema(Schema):
    id = fields.UUID()
    duct_temperature_c = fields.Float()
    duct_pressure = fields.Float()
    battery_level = fields.Float()
    rssi = fields.Integer()
    percent_open = fields.Integer()
    motor_run_time = fields.Integer()
    lights = fields.Integer()
    created_at = fields.DateTime(load_only=True)

    vent = fields.Relationship(
        related_url="/api/vent-sensor-readings/{vent_sr_id}/vent",
        related_url_kwargs={'vent_sr_id': '<id>'},
        many=False,
        include_data=True,
        type_="vents"
    )


    class Meta:
        type_ = 'vent-sensor-readings'
        inflect = dasherize

class VentStateSchema(Schema):
    id = fields.UUID()
    percent_open = fields.Integer(validate=validates_percent)
    lightstrip = fields.Integer()
    reporting_interval_ms = fields.Integer(validate=validates_unsigned16)
    motor_max_rotate_time_ms = fields.Integer(validate=validates_unsigned16)
    demo_mode = fields.Integer(validate=validates_unsigned16)
    motor_open_duty_cycle_percent = fields.Integer(validate=validates_percent)
    motor_close_duty_cycle_percent = fields.Integer(validate=validates_percent)
    sub_ghz_radio_tx_power_mw = fields.Integer(validate=validates_unsigned16)

    vent = fields.Relationship(
        related_url="/api/vent-states/{vent_s_id}/vent",
        related_url_kwargs={'vent_s_id': '<id>'},
        many=False,
        include_data=True,
        type_="vents"
    )

    class Meta:
        type_ = 'vent-states'
        inflect = dasherize

class VentSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)
    setup_lightstrip = fields.Integer(load_only=True)

    current_state = fields.Relationship(
        related_url="/api/vents/{vent_id}/current-state",
        related_url_kwargs={'vent_id': '<id>'},
        many=False,
        include_data=True,
        type_="vent-states"
    )

    previous_state = fields.Relationship(
        related_url="/api/vents/{vent_id}/previous-state",
        related_url_kwargs={'vent_id': '<id>'},
        many=False,
        include_data=True,
        type_="vent-states"
    )

    room = fields.Relationship(
        related_url="/api/vents/{vent_id}/room",
        related_url_kwargs={'vent_id': '<id>'},
        self_url="/api/vents/{vent_id}/relationships/room",
        self_url_kwargs={'vent_id': '<id>'},
        many=False,
        include_data=True,
        type_="rooms"
    )

    sensor_readings = fields.Relationship(
        related_url="/api/vents/{vent_id}/sensor-readings",
        related_url_kwargs={'vent_id': '<id>'},
        many=True,
        include_data=False,
        type_="vent-sensor-readings"
    )

    structure = fields.Relationship(
        related_url="/api/vents/{vent_id}/structure",
        related_url_kwargs={'vent_id': '<id>'},
        self_url="/api/vents/{vent_id}/relationships/structure",
        self_url_kwargs={'vent_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    class Meta:
        type_ = 'vents'
        inflect = dasherize

class PuckAppSchema(Schema):
    id = fields.UUID()
    app_type = fields.String()
    app_state = fields.Dict()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    room = fields.Relationship(
        related_url="/api/puck-apps/{puck_app_id}/room",
        related_url_kwargs={'puck_app_id': '<id>'},
        self_url="/api/puck-apps/{puck_app_id}/relationships/room",
        self_url_kwargs={'puck_app_id': '<id>'},
        many=False,
        include_data=False,
        type_="pucks"
    )

    class Meta:
        type_ = 'puck-apps'
        inflect = dasherize

class IntegrationStructureSchema(Schema):
    id = fields.UUID()
    name = fields.String(load_only=True)
    source_id = fields.String(load_only=True)
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    thermostats = fields.Relationship(
        related_url="/api/integration-structures/{integration_structure_id}/thermostats",
        related_url_kwargs={'integration_structure_id': '<id>'},
        self_url="/api/integration-structures/{integration_structure_id}/relationships/thermostats",
        self_url_kwargs={'integration_structure_id': '<id>'},
        many=True,
        include_data=True,
        type_="thermostats"
    )

    structure = fields.Relationship(
        related_url="/api/integration-structures/{integration_structure_id}/structure",
        related_url_kwargs={'integration_structure_id': '<id>'},
        self_url="/api/integration-structures/{integration_structure_id}/relationships/structure",
        self_url_kwargs={'integration_structure_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    integration = fields.Relationship(
        related_url="/api/integration-structures/{integration_structure_id}/integration",
        related_url_kwargs={'integration_structure_id': '<id>'},
        self_url="/api/integration-structures/{integration_structure_id}/relationships/integration",
        self_url_kwargs={'integration_structure_id': '<id>'},
        many=False,
        include_data=True,
        type_="integration"
    )

    class Meta:
        type_ = 'integration-structures'
        inflect = dasherize

class IntegrationSchema(Schema):
    id = fields.UUID()
    oauth_access_token = fields.String(load_only=True)
    oauth_access_token_expires_at = fields.DateTime(load_only=True)
    oauth_access_token_scope = fields.String(load_only=True)
    integration_name=fields.String(load_only=True)
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    integration_structures = fields.Relationship(
        related_url="/api/integrations/{integration_id}/integration_structures",
        related_url_kwargs={'integration_id': '<id>'},
        self_url="/api/integration/{integration_id}/relationships/integration_structures",
        self_url_kwargs={'integration_id': '<id>'},
        many=True,
        include_data=True,
        type_="integration-structures"
    )

    user = fields.Relationship(
        related_url="/api/integrations/{integration_id}/user",
        related_url_kwargs={'integration_id': '<id>'},
        self_url="/api/integration/{integration_id}/relationships/user",
        self_url_kwargs={'integration_id': '<id>'},
        many=False,
        include_data=True,
        type_="user"
    )

    class Meta:
        type_ = 'integrations'
        inflect = dasherize

class ThermostatSchema(Schema):
    id = fields.UUID()
    make = fields.String()
    model = fields.String()
    name = fields.String()
    source_id = fields.String()
    created_at = fields.DateTime(load_only=True)
    updated_at = fields.DateTime(load_only=True)

    integration_structure = fields.Relationship(
        related_url="/api/thermostats/{thermostat_id}/integration_structures",
        related_url_kwargs={'thermostat_id': '<id>'},
        self_url="/api/thermostats/{thermostat_id}/relationships/integration_structures",
        self_url_kwargs={'thermostat_id': '<id>'},
        many=False,
        include_data=True,
        type_="integration-structures"
    )

    room = fields.Relationship(
        related_url="/api/thermostats/{thermostat_id}/room",
        related_url_kwargs={'thermostat_id': '<id>'},
        self_url="/api/thermostats/{thermostat_id}/relationships/room",
        self_url_kwargs={'thermostat_id': '<id>'},
        many=False,
        include_data=True,
        type_="rooms"
    )

    structure = fields.Relationship(
        related_url="/api/thermostats/{thermostat_id}/structure",
        related_url_kwargs={'thermostat_id': '<id>'},
        self_url="/api/thermostats/{thermostat_id}/relationships/structure",
        self_url_kwargs={'thermostat_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    thermostat_states = fields.Relationship(
        related_url="/api/thermostats/{thermostat_id}/thermostat-states",
        related_url_kwargs={'thermostat_id': '<id>'},
        many=True,
        include_data=True,
        type_="thermostat-states"
    )

    class Meta:
        type_ = 'thermostats'
        inflect = dasherize

class ThermostatStateSchema(Schema):
    id = fields.UUID()
    target_temperature_c = fields.Float()
    ambient_temperature_c = fields.Float()
    created_at = fields.DateTime(load_only=True)

    thermostat = fields.Relationship(
        related_url="/api/thermostat-states/{thermostat_states_id}/thermostats",
        related_url_kwargs={'thermostat_states_id': '<id>'},
        many=False,
        include_data=True,
        type_="thermostats"
    )

    class Meta:
        type_ = 'thermostat-states'
        inflect = dasherize

class SensorReadingSchema(Schema):
    id = fields.UUID()
    room_temperature_c = fields.Float()
    room_pressure = fields.Float()
    humidity = fields.Float()
    rssi = fields.Integer()
    message_version = fields.Integer()
    battery_level = fields.Float()
    light = fields.Integer()
    rotary_encoded_clicks = fields.Integer()
    button_pushes = fields.Integer()
    created_at = fields.DateTime(load_only=True)

    puck = fields.Relationship(
        related_url="/api/sensor-readings/{reading_id}/puck",
        related_url_kwargs={'reading_id': '<id>'},
        many=False,
        include_data=True,
        type_="pucks"
    )

    class Meta:
        type_ = 'sensor-readings'
        inflect = dasherize

class WeatherReadingSchema(Schema):
    id = fields.UUID()
    sunrise = fields.DateTime()
    sunset = fields.DateTime()
    outside_temperature_c = fields.Float()
    windspeed = fields.Float()
    wind_direction = fields.Float()
    humidity = fields.Float()
    pressure = fields.Float()
    wind_chill = fields.Float()
    condition = fields.String()
    created_at = fields.DateTime(load_only=True)

    structure = fields.Relationship(
        related_url="/api/weather-readings/{reading_id}/structure",
        related_url_kwargs={'reading_id': '<id>'},
        many=False,
        include_data=True,
        type_="structure"
    )

    class Meta:
        type_ = 'weather-readings'
        inflect = dasherize

class BeaconSightingSchema(Schema):
    id = fields.UUID()
    rssi = fields.Integer()
    txpower = fields.Integer()
    distance = fields.Integer()
    manufacturer = fields.String()
    bluetooth_name = fields.String()
    bluetooth_mac = fields.String()
    observer_wifi_mac = fields.String()
    observer_device_uuid = fields.String()
    distance_string = fields.String()
    description = fields.String()
    accuracy = fields.Float()
    created_at = fields.DateTime(load_only=True)
    beacon_uuid = fields.UUID()

    puck = fields.Relationship(
        related_url="/api/beacon-sightings/{sighting_id}/puck",
        related_url_kwargs={'sighting_id': '<id>'},
        many=False,
        include_data=True,
        type_="pucks"
    )

    device = fields.Relationship(
        related_url="/api/beacon-sightings/{sighting_id}/device",
        related_url_kwargs={'sighting_id': '<id>'},
        many=False,
        include_data=True,
        type_="devices"
    )

    class Meta:
        type_ = 'beacon-sightings'
        inflect = dasherize

class DeviceSchema(Schema):
    id = fields.UUID()
    user_agent = fields.String()

    user = fields.Relationship(
        related_url="/api/devices/{device_id}/user",
        related_url_kwargs={'device_id': '<id>'},
        many=False,
        include_data=True,
        type_="users"
    )

    beacon_sightings = fields.Relationship(
        related_url="/api/devices/{device_id}/beacon_sightings",
        related_url_kwargs={'device_id': '<id>'},
        many=True,
        include_data=True,
        type_="beacon-sightings"
    )

    class Meta:
        type_ = 'devices'
        inflect = dasherize

class HVACUnitStateSchema(Schema):
    id = fields.UUID()
    temperature = fields.Float()
    power = fields.Boolean()
    mode = fields.Integer()
    fan_speed = fields.Float()

    class Meta:
        type_ = 'hvac-unit-states'
        inflect = dasherize

class HVACUnitSchema(Schema):
    id = fields.UUID()
    make = fields.String()
    model = fields.String()
    name = fields.String()
    current_state = fields.Nested(HVACUnitStateSchema)
    previous_state = fields.Nested(HVACUnitStateSchema, load_only=True)

    structure = fields.Relationship(
        related_url="/api/hvac-units/{zone_id}/structure",
        related_url_kwargs={'zone_id': '<id>'},
        self_url="/api/hvac-units/{zone_id}/relationships/structure",
        self_url_kwargs={'zone_id': '<id>'},
        many=False,
        include_data=True,
        type_="structures"
    )

    room = fields.Relationship(
        related_url="/api/hvac-units/{hvac_unit_id}/room",
        related_url_kwargs={'hvac_unit_id': '<id>'},
        self_url="/api/hvac-units/{hvac_unit_id}/relationships/room",
        self_url_kwargs={'hvac_unit_id': '<id>'},
        many=False,
        include_data=True,
        type_="rooms"
    )

    class Meta:
        type_ = 'hvac-units'
        inflect = dasherize
