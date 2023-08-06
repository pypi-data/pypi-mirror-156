import ffmpeg


class StreamSaver:

    def __init__(self,
                 streamURL: str = '',
                 outputTemplate: str = 'output_%Y-%m-%d_%H-%M-%S.ts',
                 segmentTime: str = '01:00:00'):
        """
        :param streamURL: Stream URL
        :param outputTemplate: Output template
        :param segmentTime: Segment length
        """

        self.streamURL = streamURL
        self.outputTemplate = outputTemplate
        self.segmentTime = segmentTime

    def run(self, streamURL: str = '') -> None:
        """
        Start stream saving
        :return: None
        """

        if streamURL != '':
            self.streamURL = streamURL
        if self.streamURL != '':
            self.__stream = ffmpeg.input(
                self.streamURL
            ).output(
                self.outputTemplate,
                vcodec='copy',
                acodec='copy',
                reset_timestamps=1,
                strftime=1,
                f='segment',
                segment_time=self.segmentTime,
                segment_atclocktime=1
            ).overwrite_output(
            ).run_async()

    def stop(self) -> None:
        """
        Stop stream
        :return: None
        """
        self.__stream.terminate()

    @property
    def streamURL(self):
        return self.__streamURL

    @streamURL.setter
    def streamURL(self, streamURL: str):
        self.__streamURL = streamURL

    @property
    def outputTemplate(self):
        return self.__outputTemplate

    @outputTemplate.setter
    def outputTemplate(self, outputTemplate: str):
        self.__outputTemplate = outputTemplate

    @property
    def segmentTime(self):
        return self.__segmentTime

    @segmentTime.setter
    def segmentTime(self, segmentTime: str):
        self.__segmentTime = segmentTime

    def __str__(self):
        """Overrides the default implementation"""
        return '%s => %s (%s)' % (self.streamURL, self.outputTemplate, self.segmentTime)

