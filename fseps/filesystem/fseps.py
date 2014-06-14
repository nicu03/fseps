import os
import time
import errno
import datetime

from fuse import FuseOSError, Operations, fuse_get_context
from settings import FSEPS_PERMISSIONS_FILE_NAME


class FsEps(Operations):
    def __init__(self, root):
        self.root = root
        print self.root
    # Helpers
    # =======
    def _full_path(self, partial):
        # print partial
        # print 'some kid is trying to acess the full path'
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        # print path
        #
        # print "-----------------------"
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        print type(path), path, 'xxxxx>', type(mode), mode,'<<<'
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)

        # print dir(st)

        print '**************'
        x = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                                                        'st_gid', 'st_mode',
                                                        'st_mtime', 'st_nlink',
                                                        'st_size', 'st_uid', 'st_rdev'))
        print "-------------------->"
        # x['st_uid'] = 1001
        for k, v in x.items():
            print str(k) + "->" + str(v)
        return x

    def readdir(self, path, fh):
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@'
        print fuse_get_context()
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@'
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        dirents = [x for x in dirents if x != FSEPS_PERMISSIONS_FILE_NAME]
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        print "create file "
        print path, mode, dev
        print "done\n"
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        print "mkdir->"
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        print '\n\n statfs$$$$$$$$$$$$\n\n'
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
                                                         'f_blocks', 'f_bsize',
                                                         'f_favail', 'f_ffree',
                                                         'f_files', 'f_flag',
                                                         'f_frsize',
                                                         'f_namemax'))

    def unlink(self, path):
        dir_path, filename = os.path.split(path)
        if filename == FSEPS_PERMISSIONS_FILE_NAME:
            raise FuseOSError(errno.ENOENT)
        print "DELETED SOMETHING"
        return os.unlink(self._full_path(path))

    def symlink(self, target, name):
        return os.symlink(self._full_path(target), self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    def open(self, path, flags):
        dir_path, filename = os.path.split(path)
        if filename == FSEPS_PERMISSIONS_FILE_NAME:
            raise FuseOSError(errno.ENOENT)
        upper_bound = datetime.time(18, 0, 0)
        lower_bound = datetime.time(9, 0, 0)
        now = datetime.datetime.now().time()
        # if now > upper_bound or now < lower_bound:
        # raise FuseOSError(errno.EACCES, "adfsdfsdfas")
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        print "file created "
        dir_path, filename = os.path.split(path)
        if filename == FSEPS_PERMISSIONS_FILE_NAME:
            raise FuseOSError(errno.ENOENT)
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)
