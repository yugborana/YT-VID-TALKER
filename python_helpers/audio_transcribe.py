import asyncio
import aiofiles
import requests
import json
from urllib.parse import urlparse
from azure.storage.filedatalake.aio import DataLakeDirectoryClient, FileSystemClient
from azure.storage.filedatalake import ContentSettings
import mimetypes
import logging
from pprint import pprint
import os
import dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

API_SUBSCRIPTION_KEY = os.getenv("SARVAM_API_KEY")

class SarvamClient:
    def __init__(self, url: str):
        self.account_url, self.file_system_name, self.directory_name, self.sas_token = (
            self._extract_url_components(url)
        )
        self.lock = asyncio.Lock()
        print(f"Initialized SarvamClient with directory: {self.directory_name}")

    def update_url(self, url: str):
        self.account_url, self.file_system_name, self.directory_name, self.sas_token = (
            self._extract_url_components(url)
        )
        print(f"Updated URL to directory: {self.directory_name}")

    def _extract_url_components(self, url: str):
        parsed_url = urlparse(url)
        account_url = f"{parsed_url.scheme}://{parsed_url.netloc}".replace(
            ".blob.", ".dfs."
        )
        path_components = parsed_url.path.strip("/").split("/")
        file_system_name = path_components[0]
        directory_name = "/".join(path_components[1:])
        sas_token = parsed_url.query
        return account_url, file_system_name, directory_name, sas_token

    async def upload_files(self, local_file_paths, overwrite=True):
        print(f"Starting upload of {len(local_file_paths)} files")
        async with DataLakeDirectoryClient(
            account_url=f"{self.account_url}?{self.sas_token}",
            file_system_name=self.file_system_name,
            directory_name=self.directory_name,
            credential=None,
        ) as directory_client:
            tasks = []
            for path in local_file_paths:
                file_name = path.split("/")[-1]
                tasks.append(
                    self._upload_file(directory_client, path, file_name, overwrite)
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print(
                f"Upload completed for {sum(1 for r in results if not isinstance(r, Exception))} files"
            )

    async def _upload_file(
        self, directory_client, local_file_path, file_name, overwrite=True
    ):
        try:
            async with aiofiles.open(local_file_path, mode="rb") as file_data:
                mime_type = mimetypes.guess_type(local_file_path)[0] or "audio/wav"
                file_client = directory_client.get_file_client(file_name)
                data = await file_data.read()
                await file_client.upload_data(
                    data,
                    overwrite=overwrite,
                    content_settings=ContentSettings(content_type=mime_type),
                )
                print(f"✅ File uploaded successfully: {file_name}")
                print(f"   Type: {mime_type}")
                return True
        except Exception as e:
            print(f"❌ Upload failed for {file_name}: {str(e)}")
            return False

    async def list_files(self):
        print("\n📂 Listing files in directory...")
        file_names = []
        async with FileSystemClient(
            account_url=f"{self.account_url}?{self.sas_token}",
            file_system_name=self.file_system_name,
            credential=None,
        ) as file_system_client:
            async for path in file_system_client.get_paths(self.directory_name):
                file_name = path.name.split("/")[-1]
                async with self.lock:
                    file_names.append(file_name)
        print(f"Found {len(file_names)} files:")
        for file in file_names:
            print(f"   📄 {file}")
        return file_names

    async def download_file(self, file_name, destination_dir, new_filename=None):

        try:
            async with DataLakeDirectoryClient(
                account_url=f"{self.account_url}?{self.sas_token}",
                file_system_name=self.file_system_name,
                directory_name=self.directory_name,
                credential=None,
            ) as directory_client:
                file_client = directory_client.get_file_client(file_name)
                download_path = os.path.join(destination_dir, new_filename or file_name)

                async with aiofiles.open(download_path, mode="wb") as file_data:
                    stream = await file_client.download_file()
                    data = await stream.readall()
                    await file_data.write(data)
                print(f"✅ Downloaded: {file_name} -> {download_path}")
                return True
        except Exception as e:
            print(f"❌ Download failed for {file_name}: {str(e)}")
            return False
        
async def initialize_job():
    print("\\n🚀 Initializing job...")
    url = "https://api.sarvam.ai/speech-to-text-translate/job/init"
    headers = {"API-Subscription-Key": API_SUBSCRIPTION_KEY}
    response = requests.post(url, headers=headers)
    print("\\nInitialize Job Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 202 else response.text)

    if response.status_code == 202:
        return response.json()
    return None


async def check_job_status(job_id):
    print(f"\\n🔍 Checking status for job: {job_id}")
    url = f"https://api.sarvam.ai/speech-to-text-translate/job/{job_id}/status"
    headers = {"API-Subscription-Key": API_SUBSCRIPTION_KEY}
    response = requests.get(url, headers=headers)
    print("\\nJob Status Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 200 else response.text)

    if response.status_code == 200:
        return response.json()
    return None


async def start_job(job_id):
    print(f"\\n▶️ Starting job: {job_id}")
    url = "https://api.sarvam.ai/speech-to-text-translate/job"
    headers = {
        "API-Subscription-Key": API_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }
    data = {"job_id": job_id, "job_parameters": {"with_diarization": True}}
    print("\\nRequest Body:")
    pprint(data)

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("\\nStart Job Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 200 else response.text)

    if response.status_code == 200:
        return response.json()
    return None

import os
import asyncio
# (other imports, e.g., SarvamClient, start_job, check_job_status, etc.)

async def audio_main():
    print("\n=== Starting Speech-to-Text Processing ===")

    # Step 1: Initialize the job
    job_info = await initialize_job()
    if not job_info:
        print("❌ Job initialization failed")
        return None

    job_id = job_info["job_id"]
    input_storage_path = job_info["input_storage_path"]
    output_storage_path = job_info["output_storage_path"]

    # Step 2: Upload files
    print(f"\n📤 Uploading files to input storage: {input_storage_path}")
    client = SarvamClient(input_storage_path)
    local_files = ["audio_16Khz.mp3"]  # Replace with your audio files
    print(f"Files to upload: {local_files}")
    await client.upload_files(local_files)

    # Step 3: Start the job
    job_start_response = await start_job(job_id)
    if not job_start_response:
        print("❌ Failed to start job")
        return None

    # Step 4: Monitor job status
    print("\n⏳ Monitoring job status...")
    attempt = 1
    status = None
    while True:
        print(f"\nStatus check attempt {attempt}")
        job_status = await check_job_status(job_id)
        if not job_status:
            print("❌ Failed to get job status")
            break

        status = job_status.get("job_state")
        if status == "Completed":
            print("✅ Job completed successfully!")
            break
        elif status == "Failed":
            print("❌ Job failed!")
            break
        else:
            print(f"⏳ Current status: {status}")
            await asyncio.sleep(10)
        attempt += 1

    # Step 5: Download results
    if status == "Completed":
        print(f"\n📥 Downloading results from: {output_storage_path}")
        client.update_url(output_storage_path)

        # List all files
        files = await client.list_files()

        if not files:
            print("❌ No files found to download.")
            return None

        print(f"Files to download: {files}")
        destination_dir = "./transcribed_output"
        os.makedirs(destination_dir, exist_ok=True)

        try:
            # Get job details to map input files to output files
            job_status = await check_job_status(job_id)
            file_mapping = {
                detail["file_id"]: detail["file_name"]
                for detail in job_status.get("job_details", [])
            }

            downloaded_paths = []

            # Download files with original names (mapped)
            for file in files:
                file_id = file.split(".")[0]  # e.g., '0' from '0.json'
                if file_id in file_mapping:
                    original_name = file_mapping[file_id]
                    new_filename = f"{os.path.splitext(original_name)[0]}.json"
                    await client.download_file(
                        file,
                        destination_dir=destination_dir,
                        new_filename=new_filename,
                    )
                    downloaded_path = os.path.join(destination_dir, new_filename)
                    downloaded_paths.append(downloaded_path)
                    print(f"Downloaded and renamed {file} to {downloaded_path}")
                else:
                    # Fallback: download with the server filename
                    await client.download_file(
                        file,
                        destination_dir=destination_dir
                    )
                    downloaded_path = os.path.join(destination_dir, file)
                    downloaded_paths.append(downloaded_path)
                    print(f"Downloaded {file} to {downloaded_path}")

            if not downloaded_paths:
                print("❌ No files were downloaded.")
                return None

            print(f"Files have been downloaded to: {destination_dir}")
            print("\n=== Processing Complete ===")

            # If you expect a single transcript, return its path.
            # If multiple transcripts are possible, we return the first one but print a warning.
            if len(downloaded_paths) > 1:
                print("⚠️ Multiple transcript files detected; returning the first one.")
            return downloaded_paths[0]

        except Exception as e:
            print(f"❌ Error during file download: {e}")
            return None

    print("\n=== Processing Ended (no completed results) ===")
    return None


# Run the main function
if __name__ == "__main__":
    asyncio.run(audio_main())