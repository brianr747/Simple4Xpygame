import time
import traceback

import clients.GUI_observerclient

if __name__ == '__main__':
    try:
        obj = clients.GUI_observerclient.GUI_ObserverClient()
        obj.main()
    except:
        traceback.print_exc()
        time.sleep(5)
        raise

