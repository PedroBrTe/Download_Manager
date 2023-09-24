import requests
import threading
import argparse
from pathlib import Path
from os.path import abspath


class Main:
    def __init__(self, url: str, threads: int, out_path: str):
        self.url = url
        self.threads = threads
        self.out_path = Path(abspath(out_path))

        self.all_bytes = []
        self.workers = []

        self.main()

    def main(self):
        file_name, file_size = self.get_info(self.url)

        self.download(self.url, file_size, self.threads)

        for worker in self.workers:
            worker.start()
        for worker in self.workers:
            worker.join()

        self.save_file(file_name)

    def save_file(self, file_name):
        self.all_bytes.sort()

        path = Path(self.out_path / file_name)

        with open(path, 'wb+') as file:
            for item in self.all_bytes:
                file.write(item[1])

    def worker(self, url: str, header: dict, thread: int):
        req = requests.get(url, headers=header)
        self.all_bytes.append([thread, req.content])

    def download(self, url: str, file_size, threads: int):

        last_byte_range = 0
        for i in range(1, threads + 1):
            byte_range = i * round((int(file_size) / threads))
            if byte_range == int(file_size) - 1:
                byte_range += 1

            header = {"Range": f'bytes={last_byte_range}-{byte_range}'}

            self.workers.append(threading.Thread(target=self.worker, args=(url, header, i)))

            last_byte_range = byte_range + 1

    @staticmethod
    def get_info(url):
        req_headers = requests.head(url).headers
        file_name = url.split('/')[-1]
        size = req_headers.get('content-length')

        return file_name, size


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Download Manager",
                                     description="Install any file from the internet faster than browsers")

    parser.add_argument('-u', '--url', required=True, type=str)
    parser.add_argument('-t', '--threads', default=5, type=int)
    parser.add_argument('-o', '--output', default='.', type=str)

    args = parser.parse_args()
    Main(args.url, args.threads, args.output)

