from openai import OpenAI
import base64
import logging
import os
from dotenv import load_dotenv
import textract
from moviepy.editor import VideoFileClip
from scrapegraphai.graphs import SmartScraperGraph
import PyPDF2

logger = logging.getLogger(__name__)


# TODO: move this to a utils file
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# TODO: move this to a utils file


def extract_text(file_path):
    '''Return the text extracted from the file.

    Parameters
    ----------
    file_path : str
        The path to the file.

    Returns
    -------
    str
        The text extracted from the file.

    None
        either lack of dependence or file not found
    '''

    if not os.path.exists(file_path):
        logging.error(f'{file_path} not exist')
        return None

    file_extension = os.path.splitext(file_path)[1]
    text = None
    if file_extension.lower() == '.pdf':
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
    else:
        try:
            text = textract.process(file_path).decode('utf-8')
        except FileNotFoundError:
            basename = os.path.basename(file_path)
            logging.error(f'the type {basename} is not supported download')
            return None

    return text


def get_audio_clip(video_path, output_dir=None, bitrate='32k', sample_rate=22050):
    '''Return path to audio file of the video, with significantly smaller file size.'''
    video = VideoFileClip(video_path)
    audio_clip = video.audio
    audio_path = None
    if output_dir is None:
        audio_path = os.path.splitext(video_path)[0] + '.mp3'
    else:
        audio_path = os.path.join(output_dir, os.path.basename(video_path))
        audio_path = os.path.splitext(audio_path)[0] + '.mp3'

    # Write the audio file with specified bitrate, sample rate, and channels
    audio_clip.write_audiofile(audio_path,
                               codec='mp3',
                               bitrate=bitrate,
                               fps=sample_rate,
                               nbytes=2,
                               )

    return audio_path


class Textualization:
    def __init__(self, api_key):
        try:
            self.client = OpenAI(api_key=api_key)
            self.api_key = api_key
        except Exception as e:
            logging.error(f"OpenAI client initialization error: {e}")
            self.client = None
            self.api_key = None

    def textualize_img(self, path_or_url: str) -> str:
        if not self.client:
            logging.error("OpenAI client not initialized")
            return None

        payload = {'type': 'image_url'}

        if path_or_url.startswith("http"):
            payload['image_url'] = {"url": path_or_url}
        else:
            try:
                base64_image = encode_image(path_or_url)
                payload['image_url'] = {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            except FileNotFoundError as e:
                logging.error(f"Local image not found: {e}")
                return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe the photo in one simple sentence, including any meaningful text if present, or just explain what the image shows."
                            },
                            payload
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return None

    def textualize_audio(self, audio_path):
        '''Transcribe audio using OpenAI's Whisper model

        Parameters
        ----------
        audio_path : str
            Path to the audio file

        Returns
        -------
        str
            Transcription of the audio
        None
            If there's an error in transcription
        '''
        if not self.client:
            logging.error("OpenAI client not initialized")
            return None

        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcription.text
        except FileNotFoundError as e:
            logging.error(f"Local audio not found: {e}")
            return None
        except Exception as e:
            logging.error(f"OpenAI API error during transcription: {e}")
            return None

    def textualize_file(self, file_path, word_limit=2000):
        '''Summarize the content of a file.

        Parameters
        ----------
        file_path : str
            Path to the file.
        word_limit : int, optional
            Maximum number of words to include in the summary (default is 2000).

        Returns
        -------
        str
            Summary of the file content.
        None
            If there's an error in summarization.
        '''
        if not self.client:
            logging.error("OpenAI client not initialized")
            return None

        file_text = extract_text(file_path)
        if file_text is None:
            return None

        words = file_text.split()
        clipped_text = " ".join(words[:word_limit])
        file_name = os.path.basename(file_path)

        try:
            response = self.client.chat.completions.create(
                # TODO: change to config from a configuration file
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Summarize the attachment from the provided file name and content. Give a general idea of what it's about."},
                    {"role": "user",
                        "content": f"filename:{file_name} content:{clipped_text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error during summarization: {e}")
            return None

    def textualize_video(self, cover_img_path, video_path):
        '''Generate a summary for a video based on its cover image and audio content.

        Parameters
        ----------
        cover_img_path : str
            Path to the cover image file.
        video_path : str
            Path to the video file.

        Returns
        -------
        str
            Summary of the video content.
        None
            If there's an error in summary generation.
        '''
        img_desc, transcription = None, None

        if cover_img_path:
            img_desc = self.textualize_img(cover_img_path)

        if video_path:
            audio_path = get_audio_clip(video_path)
            transcription = self.textualize_audio(audio_path)

        try:
            response = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {
                        "role": "system",
                        "content": "Create a text description of this video based on the description of the cover image and the transcript. Sometimes either one of them will be empty. No need to mention the cover image and the transcript explicitly:"
                    },
                    {
                        "role": "user",
                        "content": f"Cover Description: {img_desc}\nAudio Transcript: {transcription}"
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(
                f"OpenAI API error during video summary generation: {e}")
            return None

    def textualize_cardlike(self, url: str, content_author: str = None, source: str = None, displayed_title: str = None, displayed_description: str = None) -> str:
        '''Generate a summary for a card-like content using SmartScraperGraph.

        Parameters
        ----------
        url : str
            The URL of the content to summarize.
        content_author : str, optional
            The author of the content.
        source : str, optional
            The source of the content.
        displayed_title : str, optional
            The displayed title of the content.
        displayed_description : str, optional
            The displayed description of the content.

        Returns
        -------
        str
            A summary of the content, or None if there was an error.
        '''
        if not self.api_key:
            logging.error("API key not available")
            return None

        graph_config = {
            "llm": {
                "api_key": self.api_key,
                "model": "openai/gpt-4o-mini",
            },
            "verbose": True,
            "headless": True,
        }

        try:
            prompt = f"Summarize information into Chinese, put it into summary. "
            if content_author:
                prompt += f"Content author: {content_author}. "
            if source:
                prompt += f"Source: {source}. "
            if displayed_title:
                prompt += f"Title: {displayed_title}. "
            if displayed_description:
                prompt += f"Description: {displayed_description}. "

            smart_scraper_graph = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config=graph_config
            )
            result = smart_scraper_graph.run()

            if "summary" not in result:
                logger.error("No summary found.")
                return None

            return result.get('summary')
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def textualize(self, msg):
        # if type is img
        # run textualize_img
        # if type is audio
        # run textualize_audio
        # if type is file
        # run textualize_file
        # if type is video
        # run textualize_video
        # if type is cardlike
        # run textualize_cardlike
        pass
        


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    # Initialize Textualization
    textualization = Textualization(api_key)

    # Test with a local image
    local_image_path = 'c:/Users/harry/Downloads/wxdump_tmp/wxid_fsy5oyqm39p312/img/FileStorage/MsgAttach/2e814e41d6151bc9c60d3aafeb3a182a/Image/2024-09/d0be449312de0dd275b32e0e65c2d360.dat_a8a3955dd1e3506393fac8ef3d6645c8..jpg'
    result = textualization.textualize_img(local_image_path)
    print(f"Local image description: {result}")

    # Test audio transcription
    audio_path = 'c:/Users/harry/Downloads/wxdump_tmp/wxid_fsy5oyqm39p312/audio/1757076404@chatroom/2023-08-14_22-50-10_0_2310805469276806530.wav'
    transcription = textualization.textualize_audio(audio_path)
    print(f"Audio transcription: {transcription}")

    # Test textualize_cardlike
    url = "http://mp.weixin.qq.com/s?__biz=Mzg4ODgwODA1NA==&mid=2247486309&idx=1&sn=c5d04e06bd4a6dad2218520b0deec7ca&chksm=cff43c7cf883b56a9259160725ec77ddaed269b990bf0e978f74e3db7b745fcf86ba04c63d0c&mpshare=1&scene=1&srcid=0529qlfZEAeOebw5JqLC20BY&sharer_shareinfo=b5d35b57dd7b67647c1370fc8b1fdae7&sharer_shareinfo_first=b5d35b57dd7b67647c1370fc8b1fdae7#rd"
    author = "刘敏谈养老"
    displayed_title = "泰和养老旗下房山良乡养老社区——泰和·睿园"
    displayed_description = "点击上方蓝字关注我们 世之长者，宜居桃园福地，以安享康泰华年。距离北京市区20公里的房山良乡泰和·睿园便是这"

    card_summary = textualization.textualize_cardlike(
        url=url,
        content_author=author,
        displayed_title=displayed_title,
        displayed_description=displayed_description
    )
    print(f"Card-like link summary: {card_summary}")

    # Assuming 'textualization' is an instance of the Textualization class
    video_content = {
        'cover_img': None,
        'video': 'c:/Users/harry/Downloads/wxdump_tmp/wxid_fsy5oyqm39p312/video/FileStorage/Video/2024-05/9245dc35ef7958d1fb63249c24cd5db9.mp4',
        'summary': 'In this video, we will explore various techniques and strategies for improving time management skills and increasing productivity in daily life and work. Expert tips and practical advice will be shared to help viewers effectively manage their time and achieve their goals.'
    }

    result = textualization.textualize_video(
        cover_img_path=video_content['cover_img'],
        video_path=video_content['video']
    )

    print(f"Video summary: {result}")

    # New test with different video content
    video_content_2 = {
        'cover_img': 'c:/Users/harry/Downloads/wxdump_tmp/wxid_fsy5oyqm39p312/video/FileStorage/Video/2024-06/381ebf7076d3a3b65c6d04262c8d8d57.jpg',
        'video': None,
        'summary': 'In this video, we will learn about the benefits of yoga and how it can improve our physical and mental health.'
    }

    result_2 = textualization.textualize_video(
        cover_img_path=video_content_2['cover_img'],
        video_path=video_content_2['video']
    )

    print(f"Video summary 2: {result_2}")

    # # Test textualize_file pptx
    # file_path = 'c:/Users/88the/OneDrive/Documents/WeChat Files/a38655162/FileStorage/File/2024-07/who is Jesus.pptx'
    # # FileStorage\\File\\2024-03\\衰老.ppt
    # summary = textualization.textualize_file(file_path)
    # print(f"File summary: {summary}")

    # Test textualize_file with the specified PDF
    file_path = r'c:\Users\harry\Documents\WeChat Files\wxid_fsy5oyqm39p312\FileStorage\File\2024-05\H1B抽中之后流程 （2023年3月更新） - H1b Legal(1).pdf'
    summary = textualization.textualize_file(file_path)
    print(f"PDF summary: {summary}")