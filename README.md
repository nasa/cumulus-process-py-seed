# cumulus-process-py-seed

[Cumulus](https://github.com/cumulus-nasa/cumulus) is a cloud-based framework for distributing and processing data, used by NASA's Distributed Active Archive Center's (DAAC's). A Cumulus workflow is made up of tasks, such as finding new data at an FTP site, downloading, publishing metadata, etc. 

[cumulus-process-py](https://github.com/cumulus-nasa/cumulus-process-py) is a Python library that makes it easy to create Cumulus tasks in Python that are primarily for processing data. The cumulus-process-py library includes convenience functions that tend to be common across processing tasks. It also provides the ability to run processing at the command line in addition to the within the Cumulus framework, which can be very valuable for development.

This repository, cumulus-process-py-seed, is a project template for creating a new Cumulus task in Python. Python is a good choice for processing data with existing code libraries because Python's subprocess library for spawning commands. This allows legacy code to be integrated into Cumulus while taking advantage of the convenience of Python for wrapping the legacy code.

### The Process class
Before delving into setting up a new task it's important to understand the basics of the cumulus_process library. The main part of the library is made up of the *Process* class which is meant to be subclassed in other projects. The processing unique to this new Process child class is defined in the *process* member function.

The Process class provides a host of functionality through the use of member functions and attributes. Entrypoints (AWS Lambda handler, Activity handler, and CLI) are also provided through the use of member functions, so that any child of the Process class will automatically inherit the functions and the entrypoints. The main advantage of using a class is that it minimizes the need for passing around a lot of variables between functions, while remaining very flexible as any of the existing functions can be overridden.

### GDAL and Geolambda
This template project utilizes [Cumulus Geolambda](https://github.com/cumulus-nasa/geolambda) to provide common geospatial libraries (e.g., proj.4, GDAL). If these libraries are not required then some of the files here can be simplified further. These are noted in the steps below.

## Creating a new cumulus-process based task

Follow the steps below to update the template files in this project in the creation of a new task. This will create a new pip-installable Python project, as well as a command line utility.

#### 1. Update setup.py and rename project folder

The setup.py file needs to be updated with the name of the project. Replace ${PROJECT} with what the name of the Python package will be. It is suggested to include preface the project name with 'cumulus_' to avoid any potential conflicts with other packages and for clarity (e.g., cumulus_modis, cumulus_aster, cumulus_mynewdatasource).

The *entry_points* field in setup allows the name of the command line interface (CLI) to be specified.
```
    entry_points={
        'console_scripts': ['${PROJECT}=${PROJECT}.main:Process.cli']
    },
```
The first part of the string, *${PROJECT}=* specifies the name of the CLI program, while the second half *${PROJECT}.main:Process.cli* specifies the path to the CLI entrypoint in your main module. For example:
```
    entry_points={
        'console_scripts': ['cumulus_mynewtask=cumulus_mynewtask.main:Process.cli']
    },
```
This will install a CLI program that can be called as **cumulus_mynewtask** and will point to the cli function in your Process class.

At this time also rename the *project* folder to match the same name as your project.

#### 2.  Write Process subclass (project/main.py)

The Process subclass will be a class specific to the Processing of a new type of data. While any of the Process members can be overridden in this subclass, most users will only need provide two functions: the *input_keys* property function, and the *process* member function.

The *input_keys* property is a way to define which files are what so they can be referenced in the *process* function. For example:
```
    @property
    def input_keys(self):
        return {
            'hdf': r"^.*hdf$",
            'thumbnail': r"^BROWSE.*hdf$",
            'meta': r"^.*met$"
        }
```
We now can reference the keys *hdf, thumbnail, and meta* in the process function to get filenames rather than have to parse the input filenames manually.

The process function is where the actual processing code goes, and is a member function of your Process subclass. An instance of your Process subclass is created for a set of input files (if the CLI is used) or message (if used within the Cumulus framework). The Process subclass is instantiated with the the input file names and/or the config information from a Cumulus message, which is stored and accessible from within the Process function.

A complete list of member functions that you can use within the process class is given in the section below, but the most commonly used will be the *fetch* and *upload* functions. There are just a few requirements when writing a new Process subclass.

- **Clean up files**: This process may be deployed as a Lambda function or as a StepFunction activity running on ECS. In this type of deployment the containers can be reused between processes so it is important that any temporary files created are deleted. Files downloaded with the self.fetch() are automatically deleted when processing is over, the developer does not need to delete these.
- **Add output files to self.output**: Any output files that will be uploaded should be added to the self.output list. All files in self.output can be uploaded at once with the self.upload_output_files() function, and they will also be deleted when processing is over. Alternately, files can be uploaded with the self.upload(filename) function without adding them to self.output, in which case they need to be manuallly deleted.
- **Return S3 URLs from process function**: The process function must return the S3 URLs for all output files that were uploaded to S3.

#### 3. Update requirements files and MANIFEST.in

The requirements.txt file already includes the reference to cumulus-process. The requirements-dev.txt file contains requirements needed for development and testing, for now it just includes the *coverage* package for testing test code coverage. Update the requirements files to include your own Python requirements needed.

The MANIFEST.in file specifies files, other than Python source files, in the project directory that should be included in the deploy. Python files are included automatically, but other scripts, executables, small data or config files, etc. should be specified in the MANIFEST file. For more info see the [Python packaging tutorial](https://packaging.python.org/tutorials/distributing-packages/#manifest-in).

#### 4. Write test payload

The included test_main.py file shoud not need modification and is configured to read in a test payload and run the process function. The example payload here is based on MODIS.
```
{
  "config": {
    "buckets": {
      "internal": "cumulus",
      "private": "cumulus",
      "public": "cumulus",
      "protected": "cumulus"
    },
    "granuleIdExtraction": "(.*)",
    "url_path": "testing/cumulus-modis",
    "files_config": [
      {
        "regex": "^M.*\\.hdf$"
      },
      {
        "regex": "^M.*\\.hdf.met$"
      },
      {
        "regex": "^M.*\\.jpg$"
      },
      {
        "regex": "^M.*\\.meta\\.xml$"
      }
    ]
  },
  "input": [
    "s3://cumulus/testdata/modis/MOD09GQ.A2017001.h11v04.006.2017014010124.hdf",
    "s3://cumulus/testdata/modis/MOD09GQ.A2017001.h11v04.006.2017014010124.hdf.met"
  ]
}
```

There are several important pieces in the payload. The first is the list of input files. These could be local files, but it would make it difficult to test unless the data was included in the repository. For large data files this is not recommended. Instead, these can be put on an S3 bucket and the test process will fetch and process them.

The config section of the payload specifies the buckets to be used, as well as the files_config section. These fields are used in conjunction to determine where files should be published to. The Process.get_publish_info(filename) function will iterate through the regexes in files_config to find a matching file, then will use the *bucket* and *url_path* fields to generate the complete s3 URL. If this information is not provided (such as when calling from the command line with only a list of input files and no config info), then files will not be uploaded.

#### 5. Write Dockerfile and docker-compose.yml

The basic included Dockerfile simply installs the requirements files and the Python package. In this template it is using a Geolambda image which allows one to easily deploy to AWS Lambda (while including the common geospatial libraries). If geolambda is not used, then the developer will need to take care of packaging for Lambda themselves.

If the new Process subclass requires separate compiled code, then the Dockerfile is where that should be compiled and installed. This can be done in a variety of ways, but the recommended way is to install any compiled binaries with the PROJECT directory (alongside the Python files). Then, include these in the MANIFEST.in file so they are included in deployment, then call the executable from the Python code by getting the path dynamically:
```
exepath = os.path.dirname(__file__)
myexe = os.path.join(exepath, 'my.exe')
```

At the end of the Dockerfile, set the entrypoint to your CLI program specified in setup.py.
```
ENTRYPOINT ${CLI_NAME}
```

The included docker-compose provides several services for running and testing your process, as well as several services for deploying and testing to AWS Lambda. See the [docker-compose reference page](https://docs.docker.com/compose/compose-file/compose-file-v2/) for more info on docker-compose services. The image is built with
```
$ docker-compose build
```
and a specific service can be run with
```
$ docker-compose run servicename
```
The services in the included docker-compose.yml are:

- **base**: This simply builds the image, and if run will drop you into an interactive bash shell in the container
- **cumulus**: This will run the CLI program specified in your setup.py file (assuming ENTRYPOINT has been set in the Dockerfile)
- **test**: This runs the tests, with code coverage included
- **package**: This creates a zipfile of needed system libraries and Python dependencies suitable for deploying to AWS Lambda.
- **testpackage**: This runs the tests using the packaged files and a plain Amazon Linux image (see bin/ files below)
- **deploy**: This calls a deploy script to push the Lambda zip file to S3 (see bin/ files below)

#### 6. Update package/deploy scripts if using Lambda (optional)

If deploying to Lambda there are two scripts in the bin/ directory that are used for packaging and deploying, although in most cases they will not need to be edited.

- **deploy-to-s3.sh**: This script runs lambda-package.sh to create a zip file then uploads the file to s3, renamed with the version # of the package.
- **lambda-package.sh**: This file is a placeholder that just calls lambda-package-base.sh which is a script provided by Geolambda that packages the geospatial system libraries and Python packages on the system. This lambda-package.sh script can be used for performing additional steps beyond what is included in lambda-package-base.sh

#### 7. Update lambda_handler if using Lambda (optional)
The last step, if using AWS Lambda, is to update the lambda/lambda_handler.py file to import your new Process subclass from your Python package. Update the import line to import the correct package name that was set in setup.py.
```
from ${PROJECT} import MyProcess
```

## Process Command Line Interface
In addition to Lambda and Activity handlers, the Process class will automatically supply a CLI to your new Process subclass. Call it on the command line with "-h" to see online help. The CLI supports three different commands:

- **process**: This allows you to pass in a list of remote or local input files and generate local output. Useful for development.
- **payload**: This takes in a simple payload message, not a Cumulus message. Useful for testing.
- **activity**: Given an AWS SF Activity ARN, this runs a Cumulus activity (which expects Cumulus messages). Useful for production.

## Process Member functions

Below are descriptions of the Process class member functions (included properties and class methods). These can be caleld from within your *MyProcess.process()* function. They can also be overridden if needed.

### Properties

##### Process.input_keys
As described above, input_keys provides keys and file patterns so that files can be identified in the process function. This should always be overridden.
Note: In Cumulus workflows regex patterns for the input files are included. The input_keys property could be written to retrieve these regex expressions from the Cumulus message, but this is rarely necessary. The regex expressions included in the Cumulus message are specific and used for validation. The regex patterns used in the process() function are simply for indentifying types of files and as such can be more general than the detailed regexes defined in the Cumulus workflow.

##### Process.gid
The gid property returns the "Granule ID", based upon the input files. The default property tries to generate the GID using the following 3 methods, in order of preference:

- 1. If *granuleIdExtraction* is provided in the config part the message it will be used against the 1st file passed in to generate the GID.
- 2. Otherwise, it will try to determine the GID by finding a common prefix among all input files.
- 3. If there is no common prefix the GID is the filename of the first input file.

If other behavior is desired for determining GID, this property should be overridden.

### Member Functions
##### Process.__init__(input, path=None, config={})
The __init__ function is what is called to initialize a Process instance. It takes in:

- **input**: a list of input files, these can be local files or S3 URLs and are stored in self.input
- **path**: A local path to store output files and temp files. The valus is stored in self.path Defaults to a tmp directory
- **config**: The config part of a Cumulus message, which is stored in self.config

##### Process.fetch(key, remote=False)
The fetch function is used to download remote input files and store them in *self.path*. Any and all input files matching the provided key (see input_keys) are downloaded and returned as a list. If *remote=True* then the original input filenames (remote or not) will be returned, and not downloaded. This can be useful to retrieve the remote filename when local processing is not required.

##### Process.fetch_all(remote=False)
This convenience function will run Process.fetch for all keys provided in Process.input_keys and return the resulting filenames as a dictionary.

##### Process.upload_file(filename)
For the provided filename, the Process class will try and retrieve publication info about it from the Process.config dictionary. If publishing info is not available upload_file will jsut return the local filename. If publication info is available then the filename will be uploaded to the proper bucket and the S3 url will be returned. See *Process.get_publish_info(filename)* for more info.

##### Process.upload_output_files()
This function will upload all files (using Process.upload_file) for all files in the self.output list.

##### Process.clean_downloads(), Process.clean_output(), Process.clean_all()
Process.clean_downloads will delete all downloaded files (these are stored in self.downloads by the Process.fetch function).
Process.clean_output will delete all local output files.
Process.clean_all will call the above two functions.

##### Process.get_publish_info(filename)
Using the passed in filename and the Process.config information, this will generate the S3 URL the file should be uploaded to, as well as the http URL that can be used to access it. The URL may to a publicly available bucket, or may be a private bucket accessible only through the URL.
```
{
    "s3": "s3://bucket/path/myfile.dat",
    "http": "http://mydomain.com/path/myfile.dat"
}
```

### Class Methods

##### Process.dicttoxml(meta, pretty=False, root='Granule')
This function takes in a Python dictionary and converts it to XML. This was written to create XML files suitable for posting to the NAS Common Metadata Repository (CMR). If pretty=True then indents will be used when writing it.
Note: CMR requires data in a specific order, but Python dictionaries are unordered. This function will accept a Python ordered dictionary as well:
```
from collections import OrderedDict as od
mydict = od([('key1', 'val1'), ('key2', 'val2')])
myxml = self.dicttoxml(mydict)
```
This will create an ordered dictionary and then create the XML, ensuring that key1 in the XML comes before key2.

The related convenience function *Process.write_metadata(meta, fout, pretty=False)* will convert a metadata dictionary to XML and write it to a file named *fout*

##### Process.run_command(cmd)
This takes in a string command and spawns it using subprocess. Output will be logged and if an error occurs it will throw a RuntimeError.

##### Process.gunzip(filename, remove=False)
This function takes in a gzipped file and unzips it, creating a new file. If remove=True the original file will be deleted after.

##### Process.basename(filename)
This returns the basename of the file, without the path and without the extension.

### Handlers
These are handlers (aka Entrypoints) that can be used to perform a complete run. They are all class methods.

##### Process.run(*args, **kwargs, noclean=False)
The run function combines the initialization of a Process class, running the *process()* function, and cleaning up the input and output files afterward (if noclean=False). All of the other handlers end up calling this function.

##### Process.handler(event, context=None, path=None, noclean=False)
#### Process.cumulus_handler(event, context=None)
The handler function takes in a simple payload (as seen in test/payload.json), not a Cumulus message and calls Process.run().
The cumulus_handler function takes is the same as *Process.handler()* except it takes in a Cumulus message. It automatically sets noclean=False and uses a tmp directory for path. This is the entrypoint that would be used by a Lambda function.

##### Process.cli()
This is the entrypoint called by the Command Line Interface

##### Process.activity(arn=os.getenv('ACTIVITY_ARN'))
##### Process.cumulus_activity(arn=os.getenv('ACTIVITY_ARN'))
This is the handler that is called to run an AWS Step Function activity. Pass in the ARN for the Activity and tasks will be consumed, instantiating a new Myprocess instance for each message.

