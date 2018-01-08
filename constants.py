DBUS_OBJECT_MANAGER_PATH = '/'
DBUS_OBJECT_MANAGER_INTERFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'

BLUEZ_SERVICE = 'org.bluez'
BLUEZ_ADAPTER_PATH = '/org/bluez/hci0' # path to `adapter` object in blueZ process
BLUEZ_ADAPTER_INTERFACE = 'org.bluez.Adapter1'
BLUEZ_DEVICE_INTERFACE = 'org.bluez.Device1'
BLUEZ_GATT_SERVICE_INTERFACE = 'org.bluez.GattService1'
BLUEZ_GATT_CHARACTERISTIC_INTERFACE = 'org.bluez.GattCharacteristic1'


# Nuimo Service Fingerprints
NUIMO_SERVICE_UUID = 'f29b1525-cb19-40f3-be5c-7241ecb82fd2'
LEGACY_LED_MATRIX_SERVICE = 'f29b1523-cb19-40f3-be5c-7241ecb82fd1'
UNNAMED1_SERVICE_UUID = '00001801-0000-1000-8000-00805f9b34fb'
UNNAMED2_SERVICE_UUID = '0000180a-0000-1000-8000-00805f9b34fb'
BATTERY_SERVICE_UUID = '0000180f-0000-1000-8000-00805f9b34fb'


NUIMO_SERVICE_UUIDS = [
    NUIMO_SERVICE_UUID,
    LEGACY_LED_MATRIX_SERVICE,
    UNNAMED1_SERVICE_UUID,
    UNNAMED2_SERVICE_UUID,
    BATTERY_SERVICE_UUID
]