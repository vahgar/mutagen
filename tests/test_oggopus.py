import os
import shutil
from tempfile import mkstemp

from mutagen._compat import BytesIO
from mutagen.oggopus import OggOpus, OggOpusInfo, delete
from mutagen.ogg import OggPage
from tests import TestCase
from tests.test_ogg import TOggFileTypeMixin


class TOggOpus(TestCase, TOggFileTypeMixin):
    Kind = OggOpus

    def setUp(self):
        original = os.path.join("tests", "data", "example.opus")
        fd, self.filename = mkstemp(suffix='.opus')
        os.close(fd)
        shutil.copy(original, self.filename)
        self.audio = self.Kind(self.filename)

    def tearDown(self):
        os.unlink(self.filename)

    def test_length(self):
        self.failUnlessAlmostEqual(self.audio.info.length, 11.35, 2)

    def test_misc(self):
        self.failUnlessEqual(self.audio.info.channels, 1)
        self.failUnless(self.audio.tags.vendor.startswith("libopus"))

    def test_module_delete(self):
        delete(self.filename)
        self.scan_file()
        self.failIf(self.Kind(self.filename).tags)

    def test_mime(self):
        self.failUnless("audio/ogg" in self.audio.mime)
        self.failUnless("audio/ogg; codecs=opus" in self.audio.mime)

    def test_invalid_not_first(self):
        page = OggPage(open(self.filename, "rb"))
        page.first = False
        self.failUnlessRaises(IOError, OggOpusInfo, BytesIO(page.write()))

    def test_unsupported_version(self):
        page = OggPage(open(self.filename, "rb"))
        data = bytearray(page.packets[0])

        data[8] = 0x03
        page.packets[0] = bytes(data)
        OggOpusInfo(BytesIO(page.write()))

        data[8] = 0x10
        page.packets[0] = bytes(data)
        self.failUnlessRaises(IOError, OggOpusInfo, BytesIO(page.write()))

    def test_preserve_non_padding(self):
        self.audio["FOO"] = ["BAR"]
        self.audio.save()

        extra_data = b"\xde\xad\xbe\xef"

        with open(self.filename, "r+b") as fobj:
            OggPage(fobj)  # header
            page = OggPage(fobj)
            data = OggPage.to_packets([page])[0]
            data = data.rstrip(b"\x00") + b"\x01" + extra_data
            new_pages = OggPage.from_packets([data], page.sequence)
            OggPage.replace(fobj, [page], new_pages)

        OggOpus(self.filename).save()

        with open(self.filename, "rb") as fobj:
            OggPage(fobj)  # header
            page = OggPage(fobj)
            data = OggPage.to_packets([page])[0]
            self.assertTrue(data.endswith(b"\x01" + extra_data))
