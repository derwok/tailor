# tailor
A wrapper for ```tail -F``` that keeps a list of the last used files and allows to chose via simple menu

## Further Features
* Respects terminal width & height (but only once at launch time! Not dynamically)
* If access to file is not granted, tries to 'sudo tail -F'
* File pathes are normalized and duplicates are removed on every call
* Files are sorted "last used to top"


## Usage
### tailor [-h | --help]
Show help

### tailor [file]
Call tail -F on the file

Remembers last "x" files in ~/.tailor

### tailor
If called without any parameters, tailor presents a last-recently-used menu with the last files sent to tailor. 

* Press letter in front of file name to ```tail -F``` this file
* Press "Backspace" to toggle tail <=> delete mode. Delete mode allows to delete a line from menu
* Press ESC or Ctrl+C to end tailor's menu mode

Example:

    $ tailor
    [0] /home/4min/www/4minitz/log/4minitz.log
    [1] /var/log/apache2/other_vhosts_access.log
    [2] /var/log/apache2/error.log
    [3] /var/log/supervisor/supervisord.log
