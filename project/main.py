from cumulus_process import Process


class MyProcess(Process):
    """ A MODIS Process """

    @property
    def input_keys(self):
        return {
            'hdf': r"^.*hdf$",
            'thumbnail': r"^BROWSE.*hdf$",
            'meta': r"^.*met$"
        }

    def process(self):
        """ Process granule input file(s) into output file(s) """

        # get main data file name (remote name)
        hdf_fname = self.fetch('hdf', remote=True)[0]

        # download metadata file, there should  be only one
        meta_fname = self.fetch('meta')[0]

        # perform some processing here
        output_fname = some_process(hdf_fname, meta_fname)

        # add output file to the output list
        self.output.append(output_fname)

        # upload all files in self.output
        outputs = self.upload_output_files()

        # return list of uploaded URLs
        return outputs
