import os
import shutil
import unittest
from pywxdump.dbpreprocess.parsingMSG import ParsingMSG as parsor
# import pywxdump.dbpreprocess.transcripting as transcripting


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create temporary source and destination folders
        self.merge_db_path = "c:\\Users\\jianl\\Downloads\\pywxdumpv3027\\wxdump_tmp\\a38655162\\merge_all.db"
        self.db_parser = parsor(self.merge_db_path)

    def tearDown(self):
        # remove empty WL_transcription table
        transcripts = list(self.db_parser.get_transcript())
        ids = [transcript[0] for transcript in transcripts]
        self.db_parser.delete_transcript(ids)

    def test_add_transcript(self):
        self.db_parser.add_transcript(1112, 'transcript2')
        transcripts = list(self.db_parser.get_transcript())
        self.assertEqual(len(transcripts), 1)

    def test_get_all_transcript(self):
        transcripts = list(self.db_parser.get_transcript())
        self.assertTrue(type(transcripts) == list)

    def test_delete_transcript(self):
        transcripts = list(self.db_parser.get_transcript())
        ids = [transcript[0] for transcript in transcripts]
        self.db_parser.delete_transcript(ids)
        transcripts = list(self.db_parser.get_transcript())
        self.assertEqual(len(transcripts), 0)

    def test_transcript_single_audio_file(self):
        transcript = self.db_parser.transcript_audio(
            'c:/Users/jianl/Downloads/pywxdumpv3027/wxdump_tmp/a38655162/audio/26105312990@chatroom/2024-05-12_20-46-18_0_7894654590360025440.wav')
        self.assertIsNotNone(transcript)
        self.assertTrue(len(transcript) > 0)
        self.assertAlmostEqual(transcript, "This is the transcript")

    def test_is_voice_msg_has_transcript(self):
        # because db is empty, all is none
        self.assertFalse(self.db_parser.is_voice_msg_has_transcript(1111))

    def test_this_voice_msg_has_transcript(self):
        self.db_parser.add_transcript(1112, 'transcript2')
        self.assertTrue(self.db_parser.is_voice_msg_has_transcript(1112))

    def test_transciprt_single_voice_msg(self):
        # make sure this file exist to pass
        msg_id = 7894654590360025440
        transcripts = list(
            self.db_parser.transcript_voice_msgs_from_ids([msg_id]))
        self.assertTrue(transcripts is not None)
        self.assertAlmostEqual(transcripts[0], "This is the transcript")
        self.assertEqual(len(transcripts), 1)

    def test_transcript_two_voice_msgs(self):
        msg_ids = [8414465746626167939, 7894654590360025440]
        transcripts = list(
            self.db_parser.transcript_voice_msgs_from_ids(msg_ids))
        self.assertTrue(transcripts is not None)
        self.assertAlmostEqual(transcripts[0], "This is the transcript")
        self.assertAlmostEqual(transcripts[1], "This is the transcript")
        self.assertEqual(len(transcripts), 2)

    def test_transcript_all_and_save_to_db(self):
        self.db_parser.transcript_all_and_save_to_db()
        results = list(self.db_parser.get_transcript())
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
