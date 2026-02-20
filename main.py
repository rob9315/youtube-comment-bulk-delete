import os
import re
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class CommentDeleter:
    commentDir = ""
    extDir = "/Takeout/YouTube and YouTube Music/comments/"
    deleteds_file = None
    deleted = []

    def __init__(self):
        self.commentDir = input("Path to takeout dump main folder: ") + self.extDir
        deleteds_file_path = self.commentDir + "deleted.txt"
        if os.path.isfile(deleteds_file_path):
            with open(deleteds_file_path, "r", encoding="utf8") as deleteds_file:
                self.deleted = [x for x in deleteds_file.read().splitlines() if not x == ""]
        self.deleteds_file = open(deleteds_file_path, "a" if os.path.isfile(deleteds_file_path) else "x", encoding="utf8")
    
    def __del__(self):
        if self.deleteds_file:
            self.deleteds_file.close()

    def delete(self):
        for e in os.scandir(self.commentDir):
            if not e.is_file():
                continue
            if not e.path.endswith(".csv"):
                continue
            with open(e.path, "r", encoding="utf8") as comments_file:
                contents = comments_file.read()
                commentIds = [line.split(',')[0] for line in contents.splitlines()[1:]]

                api_service_name = "youtube"
                api_version = "v3"
                client_secrets_file = "creds.json"
                scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes
                )
                credentials = flow.run_console()
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, credentials=credentials
                )
                self.delete_comments(commentIds, youtube)

    def delete_comments(self, ids, client):
        for id in ids:
            print(f"deleting {id}... ", end='')
            if id in self.deleted:
                print("already delted")
                continue
            try:
                request = client.comments().delete(id=id)
                request.execute()
                deleted += [id]
                self.deleteds_file.write(f"{id}\n")
                print("Success")
            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    obj = CommentDeleter()
    obj.delete()
