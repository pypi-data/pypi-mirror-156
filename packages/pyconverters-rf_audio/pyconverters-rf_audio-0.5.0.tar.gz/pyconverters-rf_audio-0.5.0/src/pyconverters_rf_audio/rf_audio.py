import os
import threading
from functools import lru_cache
from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
from time import sleep, time
from typing import Type, List, cast

import requests
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile
from yt_dlp import YoutubeDL


class RFAudioParameters(ConverterParameters):
    pass


CB_QUEUES = {}


class RFAudioConverter(ConverterBase):
    """RFAudio converter ."""

    def convert(
        self, source: UploadFile, parameters: ConverterParameters
    ) -> List[Document]:
        params: RFAudioParameters = cast(RFAudioParameters, parameters)

        urls = []
        tunnel = run_webhook_server("localhost", 5001)

        inputs = source.file.readlines()
        for line in inputs:
            line = (
                str(line, "utf-8").strip() if isinstance(line, bytes) else line.strip()
            )
            if line:
                urls.append(line)

        docs = {}
        if urls:
            with TemporaryDirectory() as tmpdir:
                ydl_opt = {
                    "outtmpl": tmpdir + "/%(id)s.%(ext)s",
                    "noplaylist": True,
                    "id": True,
                    "extractaudio": True,
                    # 'audioformat': 'flac',
                    "preferffmpeg": True,
                    "format": "bestaudio/best",
                    # 'download_archive': 'downloaded_songs.txt',
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "wav",
                        }
                    ],
                    "postprocessor_args": {
                        "extractaudio+ffmpeg_o1": ["-ar", "8000", "-ac", "1"]
                    },
                }
                tmp_dir = Path(tmpdir)
                with YoutubeDL(ydl_opt) as ydl:
                    for url in urls:
                        ret = ydl.extract_info(url, download=False)
                        doc = Document(identifier=ret["id"], title=ret["title"])
                        doc.properties = {"fileName": source.filename}
                        doc.metadata = {"url": url}
                        docs[ret["id"]] = doc
                        if ret.get("description", ""):
                            doc.metadata["description"] = ret["description"]
                    ret = ydl.download(urls)

                    if ret == 0:
                        wav_files = list(tmp_dir.glob("*.wav"))
                        cb_queue = Queue()
                        uids = []
                        for wav_file in wav_files:
                            wav_url = f"{tunnel.public_url}/files/{tmp_dir.name}/{wav_file.name}"
                            cb_url = f"{tunnel.public_url}/callback"

                            resp = requests.post(
                                "https://app.deeptranscript.com/api/transcriptions/",
                                json={
                                    "recording": wav_url,
                                    "recordingFormat": "wav",
                                    "callbackUrl": cb_url,
                                    "language": "fr",
                                },
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                                },
                            )
                            if resp.ok:
                                result = resp.json()
                                uid = result["uid"]
                                doc = docs[wav_file.stem]
                                doc.properties["uid"] = uid
                                uids.append(uid)
                                CB_QUEUES[uid] = (cb_queue, tmp_dir)
                                cb_queue.put(wav_file)
                        join_queue(cb_queue, 300)
                        for uid in uids:
                            del CB_QUEUES[uid]
                        for doc in docs.values():
                            uid = doc.properties.get("uid", None)
                            if uid is not None:
                                txt_file = tmp_dir / f"{uid}.txt"
                                if txt_file.exists():
                                    with txt_file.open("r") as fin:
                                        doc.text = fin.read()
        return list(docs.values())

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return RFAudioParameters


class Pending(Exception):
    "Exception raised by Queue.put(block=0)/put_nowait()."
    pass


def join_queue(q: Queue, timeout=None):
    q.all_tasks_done.acquire()
    try:
        if timeout is None:
            while q.unfinished_tasks:
                q.all_tasks_done.wait()
        elif timeout < 0:
            raise ValueError("'timeout' must be a positive number")
        else:
            endtime = time() + timeout
            while q.unfinished_tasks:
                remaining = endtime - time()
                if remaining <= 0.0:
                    raise Pending
                q.all_tasks_done.wait(remaining)
    finally:
        q.all_tasks_done.release()


from flask import Flask, request, send_from_directory
from pyngrok import ngrok

app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def webhook_handler():
    result = request.json
    state = result["state"]
    uid = result["uid"]
    cb_queue, tmp_dir = CB_QUEUES.get(uid)
    if state == "done":
        txt_file = tmp_dir / f"{uid}.txt"
        speeches = result["speeches"]
        with txt_file.open("a") as fout:
            for speech in speeches:
                fout.write(speech["formattedText"] + "\n")
    wav_file = cb_queue.get()
    cb_queue.task_done()
    return "OK"


@app.route("/files/<path:filename>", methods=["GET"])
def getfile(filename):
    return send_from_directory("/tmp", filename)


@lru_cache(maxsize=None)
def run_webhook_server(host, port):
    threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=True, use_reloader=False)
    ).start()
    sleep(5)
    return ngrok.connect(str(port), bind_tls=True)
