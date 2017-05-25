__version__ = "0.0.9"
__status__ = "Development"
__license__ = "MIT"

from pysphere import VIServer
import time
import sys
import signal
try:
    import argparse
except:
    print("Update to version 2.7 or install argparse")
    sys.exit(1)
import logging

def signal_handler(signal, frame):
    logger.warn("Caught Ctrl+C")
    logger.warn("Will attempt a graceful exit")
    sys.exit(0)

def logger_init(verbose=False, logPath=None):
    """Logger Initialization
    verbose: Nimmt einen Bool entgegen. Dieser sendet den output auf die Konsole.
    logPath: Nimmt einen String entgegen. Ort der Logdatei. Wird automatisch angelegt oder haengt Logs an.

    Gibt logger zurueck.
    """
    logger = logging.getLogger('USV2')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if verbose or logPath is None:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if logPath:
        fh = logging.FileHandler(logPath)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def vConnect(VIHost, VIUser, VIPassword):
    """Verbindungs Funktion zum Server
    Baut eine Verbindung mit VCS Server auf und speichert die Verbindungsinformationen in der VISerever variable des Typs "VIServer".
    """
    logger.info("Connecting to vSphere: " + VIHost)
    VirtualServerInstance = VIServer()
    VirtualServerInstance.connect(VIHost, VIUser, VIPassword)
    if VirtualServerInstance:
        logger.info("Connected to vSphere: " + VIHost)
        logger.info(VirtualServerInstance.get_api_type() + " API " + VirtualServerInstance.get_api_version())
        return VirtualServerInstance
    else:
        logger.error("Connection to the vSphere failed.")
        sys.exit(2)


def vDisconnect(VIServer):
    """Verbindungs-Trennungs Funktion
    Baut die Verbindung mit dem VCS Server ab.
    """
    logger.info("Disconnecting from vSphere")
    return VIServer.disconnect()

def VirtualMachine_List(VIServer, VirtualMachineList):
    """
    Listet Virtuelle Maschienen
    """
    logger.info("Listing found Virtual Machines using provided information")
    logger.info("Virtual Machine count is " + str(len(VirtualMachineList)))

    for VirtualMachineEntry in range(len(VirtualMachineList)):
        VirtualMachine = VIServer.get_vm_by_path(VirtualMachineList[VirtualMachineEntry])
        logger.info("("+ str(VirtualMachineEntry+1) +"/"+ str(len(VirtualMachineList)) +") " + VirtualMachine.get_property("name"))

def VirtualMachine_Start(VIServer, VirtualMachineList):
    """VMs Start Funktion
    Faehrt die OS auf den VMs asyncron hoch.
    Wenn die VMWare Tools nich installiert sind, werden die VMs ignoriert und dieser vorfall gelogt.
    """
    for VirtualMachineEntry in VirtualMachineList:
        VirtualMachine = VIServer.get_vm_by_path(VirtualMachineEntry)
        if VirtualMachine.is_powered_off():
            try:
                logger.info("Sending Power-On signal to " + VirtualMachine.get_property("name"))
                VirtualMachine.power_on()
            except:
                logger.error(VirtualMachine.get_property("name") + " could not be turned on")


def VirtualMachine_Shutdown(VIServer, VirtualMachineList):
    """VMs Shutdown Funktion
    Faehrt die OS auf den VMs asyncron runter.
    Wenn die VMWare Tools nich installiert sind, werden die VMs mit dem Befehl "Power Off" heruntergefahren.
    """
    for VirtualMachineEntry in VirtualMachineList:
        VirtualMachine = VIServer.get_vm_by_path(VirtualMachineEntry)
        if VirtualMachine.is_powered_on():
            try:
                logger.info("Sending Guest Shutdown signal to " + VirtualMachine.get_property("name"))
                VirtualMachine.shutdown_guest()
            except:
                logger.error("Problem with VMWare Tools on " + VirtualMachine.get_property("name"))
                logger.warn("Switching to Power-Off sequence on " + VirtualMachine.get_property("name"))
                VirtualMachine.power_off(sync_run=False)


def VirtualMachine_PowerOff(VIServer, VirtualMachineList):
    """VMs Power Off Funktion
    Faehrt VMs mit dem Befehl "Power Off" asyncron runter.
    """
    for VirtualMachineEntry in VirtualMachineList:
        VirtualMachine = VIServer.get_vm_by_path(VirtualMachineEntry)
        if VirtualMachine.is_powered_on():
            try:
                logger.info("Sending Power-Off signal to " + VirtualMachine.get_property("name"))
                VirtualMachine.power_off(sync_run=False)
            except:
                logger.critical("Power-Off signal failed on " + VirtualMachine.get_property("name"))


def VirtualMachine_ServerList(VIServer, categories, cluster=None, status=None, tagID=201):
    """
    Die Funktion hollt sich als erstes die Informationen "customValue" und "config.files.vmPathName" aka. den Pfad aller VMs aus dem Server raus.
    Daraus werden nur die VMs genomen, die den Schluessel 201 aka. "Shutdown-Reihenfolge" besitzen und der mit den uebergeben Parametern uebereinstimmt.

    Folgend darauf werden alle laufende VMs gelistet. Diese werden dann mit den VMs die zufor ausgefiltert worden sind abgegliechen und als eine Liste zurueck gegeben.
    """

    if status and cluster:
        VirtualMachineFetchResult = VIServer.get_registered_vms(cluster=cluster, status=status)
        logger.info("Fetching Virtual Machines from cluster: '" + cluster + "' with the status: '" + status + "'")
    elif status and cluster is None:
        VirtualMachineFetchResult = VIServer.get_registered_vms(status=status)
        logger.info("Fetching Virtual Machines with the status: '" + status + "'")
    elif cluster and status is None:
        VirtualMachineFetchResult = VIServer.get_registered_vms(cluster=cluster)
        logger.info("Fetching Virtual Machines from cluster: '" + cluster + "'")
    else:
        VirtualMachineFetchResult = VIServer.get_registered_vms()
        logger.info("Fetching all Virtual Machines from vSphere")

    if categories and tagID:
        logger.info(
            "Filtering Virtual Machines by annotation ID: " + str(tagID) + " with the following content: " + ", ".join(
                categories))
        VirtualMachineList = []
        VirtualMachinesWithAnnotation = []
        VirtualMachinesRelated = []
        ProperetyNames = ['customValue', 'config.files.vmPathName', 'config.template']
        ProperetyResults = VIServer._retrieve_properties_traversal(property_names=ProperetyNames, obj_type="VirtualMachine")

        for obj in ProperetyResults:
            VirtualMachine = {'annotations': []}
            VirtualMachineList.append(VirtualMachine)

            if not hasattr(obj, "PropSet"):
                continue
            for prop in obj.PropSet:
                if prop.Name == "name":
                    VirtualMachine['name'] = prop.Val
                elif prop.Name == "config.files.vmPathName":
                    VirtualMachine['path'] = prop.Val
                elif prop.Name == "config.template":
                    VirtualMachine['is_template'] = prop.Val
                elif prop.Name == "customValue":
                    for annotation in prop.Val.CustomFieldValue:
                        VirtualMachine['annotations'].append((annotation.Key, annotation.Value))

        for VirtualMachine in VirtualMachineList:
            if not VirtualMachine['is_template']:
                for annotation in VirtualMachine['annotations']:
                    if tagID in annotation:
                        for category in categories:
                            if category in annotation:
                                VirtualMachinesWithAnnotation.append(VirtualMachine['path'])

        for i in VirtualMachinesWithAnnotation:
            if i in VirtualMachineFetchResult:
                VirtualMachinesRelated.append(i)

        return VirtualMachinesRelated
    else:
        return VirtualMachineFetchResult


parser = argparse.ArgumentParser(description='Automatisierter Shutdown von ESX-Hosts und VMs bei einem Stormausfall')
parser.add_argument('-u', '--user', dest='VIUser', required=True, help='vSphere User')
parser.add_argument('-p', '--paswsword', dest='VIPassword', required=True, help='vSphere User Password')
parser.add_argument('-H', '--host', dest='VIHost', required=True, help='vSphere Host Adress')
parser.add_argument('-t', '--tag', dest='VICategories', nargs='*', help='Tag to be used to filter Virtual Machines')
parser.add_argument('-id', '--id', dest='tagID', type=int, default=201, help='ID of the Tag Field used by vSphere (default: 201)')
parser.add_argument('-w', '--wait', dest='maxWaitVMs', metavar='N', type=int, default=900, help='Seconds to wait between the Shutdown and Kill sequence (default:900)')
parser.add_argument('-a', '--action', choices=['shutdown', 'kill', 'start', 'list'], dest='VMAction', default="list", help='Action to perform on found Virtual Machines')
parser.add_argument('-s', '--status', choices=['poweredOn', 'poweredOff', 'suspended'], dest='VIStatus', help='Status used to search for Virtual Machines')
parser.add_argument('-c', '--cluster', dest='VICluster', help='Cluster where Virtual Machines will be searched')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='will print the logs to STDOUT if the -o/--out option is provided.')
parser.add_argument('-o', '--out', dest='logPath', help='Path to the file where the logs will be stored.')

if __name__ == "__main__":
    args = parser.parse_args()
    global logger
    logger = logger_init(args.verbose, args.logPath)
    logger.info("Logger was successfully initialized")
    signal.signal(signal.SIGINT, signal_handler)
    VIServer = vConnect(args.VIHost, args.VIUser, args.VIPassword)

    if 'list' in args.VMAction:
        VirtualMachine_List(VIServer, VirtualMachine_ServerList(VIServer, args.VICategories, args.VICluster, args.VIStatus, args.tagID))
    elif 'start' in args.VMAction:
        VirtualMachine_Start(VIServer, VirtualMachine_ServerList(VIServer, args.VICategories, args.VICluster, args.VIStatus, args.tagID))
    elif 'shutdown' in args.VMAction:
        VirtualMachine_Shutdown(VIServer, VirtualMachine_ServerList(VIServer, args.VICategories, args.VICluster, args.VIStatus, args.tagID))
        logger.info("Waiting " + str(args.maxWaitVMs) + " seconds before sending Power-Off Signal to the Virtual Machines")
        time.sleep(args.maxWaitVMs)
        VirtualMachine_PowerOff(VIServer, VirtualMachine_ServerList(VIServer, args.VICategories, args.VICluster, args.VIStatus, args.tagID))
    elif 'kill' in args.VMAction:
        VirtualMachine_PowerOff(VIServer, VirtualMachine_ServerList(VIServer, args.VICategories, args.VICluster, args.VIStatus, args.tagID))
    else:
        args
        parser.print_help()

    vDisconnect(VIServer)