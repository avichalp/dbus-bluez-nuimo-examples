import dbus
import json
import re
import dbus.mainloop.glib

from gi.repository import GObject
from pprint import pprint

import constants


devices = set()
connected_devices = set()
device_path = '/org/bluez/hci0/dev'
device_path_regex = re.compile('^' + device_path + '((_[A-Z0-9]{2}){6})$')
service_path_regex = re.compile(
    '^' + device_path + '((_[A-Z0-9]{2}){6})/service[0-9abcdef]{4}$'
)
characteristic_path_regex = re.compile(
    '^' + device_path + '((_[A-Z0-9]{2}){6})/service[0-9abcdef]{4}/char[0-9abcdef]{4}$'
)


# mainloop is an eventloop used for asynchronously calling
# methods on objecs exposed by blueZ service over dbus.
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


bus = dbus.SystemBus()


def get_interface(object_path, interface_name):
    ''' Gets dbus interface given the object path and the interface name.

    :param object_path: object path in dbus.
    :param interface_name: name of the dbus interface.
    '''
    proxy_bluez_object = bus.get_object(constants.BLUEZ_SERVICE, object_path)
    return dbus.Interface(proxy_bluez_object, interface_name)


def ipc(interface, method, args=None):
    '''
    Preforms IPC calls via dbus.

    :params interface: interface object that has the method to be called.
    :params method String: name to method to be called.
    '''
    method = getattr(interface, method)
    return_value = None

    if args is not None:
        try:
            return_value = method(*args)
        except Exception as e:
            # todo: improve handling
            print('[ERROR ] :::: %s' % str(e).upper())

    return return_value or method


def get_battery_level(path):
    # Todo: doesn't work with Nuimo: IOS emulator.
    # Shows read not permitted error. Test on other devices.
    # `dbus.exceptions.DBusException: org.bluez.Error.NotPermitted: Read not permitted`
    battery_gatt_iface = get_interface(
        path, constants.BLUEZ_GATT_CHARACTERISTIC_INTERFACE
    )

    battery_value = ipc(
        battery_gatt_iface,
        'ReadValue',
        ({'offset': dbus.UInt16(8, variant_level=1)},)
    )
    print('[BATTERY VALUE ] :::: ', battery_value)


def add_device(path):
    '''Connects to discovered devices.

    :param path: object path of the dbus object that represents the device.
    '''
    if device_path_regex.match(path):
        device_object = bus.get_object(constants.BLUEZ_SERVICE, path)
        device_interface = dbus.Interface(
            device_object, constants.BLUEZ_DEVICE_INTERFACE
        )
        device_properties_interface = dbus.Interface(
            device_interface, constants.DBUS_PROPERTIES_INTERFACE
        )
        device_properties_interface.connect_to_signal(
            'PropertiesChanged', device_props_change_handler,
            path_keyword='path'
        )
        devices.add(str(path))
        print('[TRYING TO CONNECT ] :::: ', path)
        connect(path)


def device_props_change_handler(sender, changed_props, invalidated_props, path):
    print('[DEVICE PROPERTY CHANGED ] ::: ', path)
    print('[CHANGED PROPERTY ] :::: ', json.dumps(changed_props, indent=2))
    print('[INVALIDATED PROPERTY ] :::: ', json.dumps(invalidated_props, indent=2))

    if 'Connected' in changed_props:
        if changed_props['Connected']:
            print('[CONNECTED ] :::: ', path)
            connected_devices.add(str(path))
        else:
            print('[DISCONNECTED ] :::: ', path)
            # todo remove device

    if 'ServicesResolved' in changed_props:
        print('[SERVICES RESOLVED ] :::: ', path)


def interface_added_handler(path, interfaces):
    print('[INTERFACE ADDED ] :::: ', path)
    object_manager_iface = get_interface(
        constants.DBUS_OBJECT_MANAGER_PATH,
        constants.DBUS_OBJECT_MANAGER_INTERFACE
    )

    all_managed_objects = object_manager_iface.GetManagedObjects()

    # Read battery level using GATT characteristic via dbus.
    battery_service_object = [
        managed_service for managed_service in all_managed_objects.items()
        if service_path_regex.match(managed_service[0]) and
        managed_service[1][
            constants.BLUEZ_GATT_SERVICE_INTERFACE
        ]['UUID'] == constants.BATTERY_SERVICE_UUID
    ]

    if battery_service_object:
        battery_service_path = battery_service_object[0][0]
        print('[BATTERY SERVICE PATH ] :::: ', battery_service_path)

        if characteristic_path_regex.match(path):
            get_battery_level(path)

    add_device(path)


def interface_removed_handler(path, interfaces):
    print('[INTERFACES REMOVED ] :::: ', path)


def property_changed_handler(interface, changed, invalidated, path):
    print('[PROPERTIES CHANGED ] :::: ', path)
    print('[CHANGED ] :::: ', json.dumps(changed, indent=2))
    print('[INVALIDATED ] :::: ', json.dumps(invalidated, indent=2))
    add_device(path)

def discover():
    adapter_interface = get_interface(
        constants.BLUEZ_ADAPTER_PATH,
        constants.BLUEZ_ADAPTER_INTERFACE
    )
    print('[STARTED DISCOVERY ] ::::')
    start_discovery = ipc(adapter_interface, 'StartDiscovery', tuple())


def discover_nuimo():
    adapter_interface = get_interface(
        constants.BLUEZ_ADAPTER_PATH,
        constants.BLUEZ_ADAPTER_INTERFACE
    )
    # Filter devices by the GATT Services they offer
    discovery_filter = {
        'Transport': 'le',
        'UUIDs':constants.NUIMO_SERVICE_UUIDS
    }
    discovery_filter = ipc(
        adapter_interface,'SetDiscoveryFilter', (discovery_filter,)
    )
    discover()


def connect(device_path):
    device_interface = get_interface(
        device_path, constants.BLUEZ_DEVICE_INTERFACE
    )
    ipc(device_interface, 'Connect', tuple())


def disconnect(device_path):
    device_interface = get_interface(
        device_path, constants.BLUEZ_DEVICE_INTERFACE
    )
    ipc(device_interface, 'Disconnect', tuple())


def pair(device_path):
    device_interface = get_interface(
        device_path, constants.BLUEZ_DEVICE_INTERFACE
    )
    ipc(device_interface, 'Pair', tuple())


bus.add_signal_receiver(
    interface_added_handler,
    dbus_interface=constants.DBUS_OBJECT_MANAGER_INTERFACE,
    signal_name='InterfacesAdded'
)


bus.add_signal_receiver(
    interface_removed_handler,
    dbus_interface=constants.DBUS_OBJECT_MANAGER_INTERFACE,
    signal_name='InterfacesRemoved'
)


bus.add_signal_receiver(
    property_changed_handler,
    dbus_interface=dbus.PROPERTIES_IFACE,
    signal_name='PropertiesChanged',
    arg0=constants.BLUEZ_DEVICE_INTERFACE,
    path_keyword='path'
)


# Start discovering bluetooth devices with hci0 adapter
discover_nuimo()

event_loop = GObject.MainLoop()
event_loop.run()
