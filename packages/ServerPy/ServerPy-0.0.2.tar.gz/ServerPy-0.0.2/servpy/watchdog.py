import time
import requests
from .utils import ping, get_unique_id
from .constants import POLLING_HEALTH, POLLING_PING, ACTIVE_STATUS, INACTIVE_STATUS, SERVER_ERROR_STATUS, SERVER_UNREACHABLE_STATUS
from .models import ServiceStatistics, StatisticsPacket, Watcher


class WatchDog(Watcher):
    def __init__(self, server_urls, poll_method, poll_endpoint, poll_freq, poll_retries, retry_delay, statistics: ServiceStatistics, *args, **kwargs) -> None:
        super().__init__(server_urls, poll_method, poll_endpoint, statistics, *args, **kwargs)
        self.frequency = poll_freq
        self.retries = poll_retries
        self.retry_delay = retry_delay
        self._id = get_unique_id()
        print(f"Woof woof (ID={self._id}). I will be watching: {self.server_url} using {self.polling_method} after every {self.frequency} seconds.")

    def __watch(self):
        url = self.server_url
        self.statistics.set_check_start()
        while(True):
            try_count = 0
            while try_count <= self.retries:
                print(f"{self._id} polling the server with try {try_count+1}..")
                packet = StatisticsPacket()
                packet.mark_start()
                try:
                    if self.polling_method == POLLING_PING:
                        if ping(url):
                            # Ping success
                            packet.set_status(ACTIVE_STATUS)
                        else:
                            packet.set_status(INACTIVE_STATUS)
                    elif self.polling_method == POLLING_HEALTH:
                        _url = url+self.polling_url
                        response = requests.get(_url)
                        if response.status_code == 200:
                            packet.set_status(ACTIVE_STATUS)
                        elif response.status_code == 500:
                            pass
                except ConnectionError as e:
                    packet.set_status(SERVER_UNREACHABLE_STATUS)
                    packet.set_response(e)
                    self.statistics.set_last_failure()
                except Exception as e:
                    packet.set_status(SERVER_ERROR_STATUS)
                    packet.set_response(str(e))
                    self.statistics.set_last_failure()
                packet.mark_end()
                self.statistics.register_packet(packet)
                self.statistics.set_last_checked_at()
                try_count+=1
                time.sleep(self.retry_delay) if self.retry_delay else None
            print(f"{self._id} going for a nap")
            time.sleep(self.frequency)
    
    def watch(self):
        self.__watch()

    