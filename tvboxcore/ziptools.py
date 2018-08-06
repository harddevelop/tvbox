
import base64, re, urllib, string, sys, zipfile, os, os.path
import logger

class ziptools:

    def extract(self, file, dir):
        logger.debug("file=%s" % file)
        logger.debug("dir=%s" % dir)
        
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)
        self._createstructure(file, dir)
        num_files = len(zf.namelist())

        for name in zf.namelist():
            logger.debug("name=%s" % name)
            if not name.endswith('/'):
                logger.debug("continue with file: "+name)
                try:
                    (path,filename) = os.path.split(os.path.join(dir, name))
                    logger.debug("path=%s" % path)
                    logger.debug("name=%s" % name)
                    os.makedirs( path )
                except:
                    pass
                outfilename = os.path.join(dir, name)
                logger.debug("outfilename=%s" % outfilename)
                try:
                    outfile = open(outfilename, 'wb')
                    outfile.write(zf.read(name))
                except:
                    logger.error("Something happened in file: "+name)

    def extractReplacingMainFolder(self, file, dir, replacement):
        logger.debug("file=%s" % file)
        logger.debug("dir=%s" % dir)

        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)
        self._createstructure(file, dir, replacement)
        num_files = len(zf.namelist())

        for name in zf.namelist():
            logger.debug("name=%s" % name)
            if not name.endswith('/'):
                logger.debug("continue with file: "+name)
                try:
                    (path,filename) = os.path.split(os.path.join(dir, name))
                    logger.debug("path=%s" % path)
                    logger.debug("name=%s" % name)
                    if replacement != '':
                        logger.debug("replace original folder: "+path)
                        path = path.replace(name[:name.find("/")],replacement)
                        logger.debug("replaced [new] folder: "+path)
                    os.makedirs(path)
                except:
                    pass
                newName = ''
                if replacement != '':
                    logger.debug("replace original name: "+name)
                    newName = name.replace(name[:name.find("/")],replacement)
                    logger.debug("replaced [new] name: "+name)
                outfilename = os.path.join(dir, newName)
                logger.debug("outfilename=%s" % outfilename)
                try:
                    outfile = open(outfilename, 'wb')
                    outfile.write(zf.read(name))
                except:
                    logger.error("Something happened in file: "+outfilename)

    def _createstructure(self, file, dir, replacement=''):
        self._makedirs(self._listdirs(file,replacement), dir)

    def create_necessary_paths(filename):
        try:
            (path,name) = os.path.split(filename)
            logger.debug("Creating dir: "+path)
            os.makedirs( path)
        except:
            pass

    def _makedirs(self, directories, basedir):
        logger.debug("basedir: "+basedir)
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                logger.debug("Creating dir: "+curdir)
                os.mkdir(curdir)

    def _listdirs(self, file, replacement=''):
        zf = zipfile.ZipFile(file)
        dirs = []
        for name in zf.namelist():
            if name.endswith('/'):
                if replacement!='':
                    subName = name[(name[1:].find('/')+1):]
                    name = replacement+subName
                logger.debug("Appended name: "+name)
                dirs.append(name)

        dirs.sort()
        return dirs
