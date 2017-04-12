#!/usr/bin/env python
import os
import re
import pprint
import sys
import subprocess as sp
from os.path import basename
from subprocess import *
from optparse import OptionParser
from os import listdir
from os.path import isfile, join
import shutil

def parseChapters(filename):
  chapters = []
  command = [ "ffmpeg", '-i', filename]
  output = ""
  m = None
  title = None
  chapter_match = None
  try:
    # ffmpeg requires an output file and so it errors
    # when it does not get one so we need to capture stderr,
    # not stdout.
    output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
  except CalledProcessError, e:
    output = e.output

  num = 1

  for line in iter(output.splitlines()):
    x = re.match(r".*title.*: (.*)", line)
    print "x:"
    pprint.pprint(x)

    print "title:"
    pprint.pprint(title)

    if x == None:
      m1 = re.match(r".*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+).*", line)
      title = None
    else:
      title = x.group(1)

    if m1 != None:
      chapter_match = m1

    print "chapter_match:"
    pprint.pprint(chapter_match)

    if title != None and chapter_match != None:
      m = chapter_match
      pprint.pprint(title)
    else:
      m = None

    if m != None:
      if title != 'Advertisement':
        chapters.append({ "name": num, "start": m.group(2), "end": m.group(3)})
      num += 1

  return chapters

def getChapters():
  parser = OptionParser(usage="usage: %prog [options] filename", version="%prog 1.0")
  parser.add_option("-f", "--file",dest="infile", help="Input File", metavar="FILE")
  (options, args) = parser.parse_args()
  if not options.infile:
    parser.error('Filename required')
  chapters = parseChapters(options.infile)
  fbase, fext = os.path.splitext(options.infile)
  path, file = os.path.split(options.infile)
  newdir, fext = os.path.splitext( basename(options.infile) )

  #remove files/folder and recreate
  if os.path.exists(path + "/" + newdir):
    shutil.rmtree(path + "/" + newdir)
  os.mkdir(path + "/" + newdir)

  for chap in chapters:
    #chap['name'] = chap['name'].replace('/',':')
    #chap['name'] = chap['name'].replace("'","\'")
    print "start:" +  chap['start']
    chap['outfile'] = path + "/" + newdir + "/" + str(int(chap['name'])) + fext
    chap['origfile'] = options.infile
    print chap['outfile']
  return chapters

def convertChapters(chapters):
    for chap in chapters:
        print "start:" +  chap['start']
        if float(chap['start']) > 3:
          chap['start'] = str(float(chap['start']) - 3)
          print('Chapstart = ' + chap['start'])
        #chap['end'] = str(float(chap['end']) + 1)
        print chap
        command = [
            "ffmpeg", '-i', chap['origfile'],
            '-vcodec', 'copy',
            '-acodec', 'copy',
            '-ss', chap['start'],
            '-to', chap['end'],
            chap['outfile']]
        output = ""
        try:
          # ffmpeg requires an output file and so it errors
          # when it does not get one
          output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
        except CalledProcessError, e:
          output = e.output
          raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    convert_path = "/convertfiles/input"
    converted_files = [f for f in listdir(convert_path) if isfile(join(convert_path, f))]
    #print(sorted(converted_files))

    write_string = ""
    filenum_list = []
    for file in converted_files:
        file_num = file.split('.')
        #print(file_num[0])
        filenum_list.append(file_num[0])

    print(sorted(filenum_list, key=int))

    for file_num in sorted(filenum_list, key=int):
        write_string += "file '/convertfiles/input/" + file_num + ".mp4'\n"

    f = open('/tmp/concat.txt','w')
    f.write(write_string)
    f.close()

    output_folder = "/convertfiles/output"
    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #Now concat the files together into a MKV
    command_1 = [
        "ffmpeg", '-f', 'concat',
        '-safe', '0',
        '-i', '/tmp/concat.txt',
        '-c:v', 'libx264',
        '-b:v', '3100k',
        '-c:a', 'aac',
        '-b:a', '128k',
        '/convertfiles/output/output.mkv']
    output_1 = ""
    try:
      # ffmpeg requires an output file and so it errors
      # when it does not get one
      output_1 = sp.check_output(command_1, stderr=sp.STDOUT, universal_newlines=True)
    except CalledProcessError, e:
      output_1 = e.output
      raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


#filebot -rename convertfiles/output --db TheTVDB --format {n} - {s00e00} - {t} --action move --conflict override
    command_2 = [
        "filebot",
        '-rename', '/convertfiles/output/',
        '--db', 'TheTVDB',
        '--format', '{n} - {s00e00} - {t}',
        '--action', 'move',
        '--conflict', 'override']
    output_2 = ""
    try:
      # ffmpeg requires an output file and so it errors
      # when it does not get one
      output_2 = sp.check_output(command_2, stderr=sp.STDOUT, universal_newlines=True)
    except CalledProcessError, e:
      output_2 = e.output_2
      raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

if __name__ == '__main__':
  chapters = getChapters()
  convertChapters(chapters)
