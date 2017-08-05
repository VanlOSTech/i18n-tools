#!/usr/bin/env python
#coding:utf8

import argparse
import os
import sys
import platform
import commands
import json
import textwrap
import xml.sax
from bs4 import BeautifulSoup

def load_translated_po_to_list(filename):
    msglist = []
    file = open(filename, 'r')
    try:
        data = file.read()
    finally:
        file.close()
    targets = data.split("msgid \"")
    for target in targets:
        if "msgstr " in target:
            results = target.replace("\"\n\n", "").split("\"\nmsgstr \"")
            #print(results)
            msgid = results[0]
            msgstr = results[1]
            #print(msgid, msgstr)
            dic={'msgid': msgid, 'msgstr': msgstr}
            result = json.dumps(dic)
            msglist.append(result)
    return msglist

def translate_single_html_from_po(htmlfile, msgs):
    print('===================' + htmlfile + '===================')
    if os.path.isfile(htmlfile):
        html_doc = ''
        file = open(htmlfile,"r")
        try:
            html_doc = file.read()
        except Exception,e:
            print e.message
        finally:
            file.close()
        #print html_doc
        soup = BeautifulSoup(html_doc,'lxml')
        soup.encode("utf-8")
        #print soup.prettify()
        for child in soup.descendants:
            #print(type(child.string),child.string)
            for msg in msgs:
                #print msg
                s = json.loads(msg)
                #print(s['msgid'], s['msgstr'])
                if s['msgstr'].strip() and s['msgid'] == child.string:
                    print('Found [%s]]'%child.string)
                    child.string = s['msgstr']
        #print(type(soup.prettify()), soup.prettify(formatter="html"))
        html_doc = ''
        html_doc = soup.prettify(formatter="html")
        #print type(html_doc)
        #print html_doc
        file = open(htmlfile, 'w')
        try:
            file.write(html_doc.encode('utf-8'))
        except Exception,e:
            print e.message
        finally:
            file.close()

def translate_html_from_po(arguments):
    msgs = load_translated_po_to_list("translate.po")
    all_results = []
    for target in arguments.targets:
        if os.path.isdir(target):
            walk_results = os.walk(target)
            for p,d,files in walk_results:
                for f in files:
                    fullpath = os.path.join(p,f)
                    sysstr = platform.system()
                    if(sysstr =="Windows"):
                        fullpath.replace('\/', '\\')
                    elif(sysstr == "Linux"):
                        fullpath.replace('\\', '\/')
                    else:
                        print ("Other System tasks")
                    all_results.append(fullpath)
        elif os.path.isfile(target):
            all_results.append(target)
        else:
            print "%s is a special file (socket, FIFO, device file), pass it..." % target
    for result in all_results:
        translate_single_html_from_po(result, msgs)

def translate_html_from_po_parser(subparsers):
    """Argument parser for translate-html-from-po command.

    translate-html-from-po [file1] [file2] ... [filen]
    """

    description = """
    Translate html from po file.
    """
    parser = subparsers.add_parser(
        'translate-html-from-po',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('targets', nargs='*', help="Directory or HTML file")
    parser.set_defaults(func=translate_html_from_po)
    return parser

def format_single_html_prettify(htmlfile):
    print('===================' + htmlfile + '===================')
    if os.path.isfile(htmlfile):
        html_doc = ''
        file = open(htmlfile,"r")
        try:
            html_doc = file.read()
        except Exception,e:
            print e.message
        finally:
            file.close()
        soup = BeautifulSoup(html_doc,'lxml')
        soup.encode("utf-8")
        html_doc = soup.prettify(formatter="html")
        #print type(html_doc)
        #print html_doc
        file = open(htmlfile, 'w')
        try:
            file.write(html_doc.encode('utf-8'))
        except Exception,e:
            print e.message
        finally:
            file.close()

def format_html_prettify(arguments):
    all_results = []
    for target in arguments.targets:
        if os.path.isdir(target):
            walk_results = os.walk(target)
            for p,d,files in walk_results:
                for f in files:
                    fullpath = os.path.join(p,f)
                    sysstr = platform.system()
                    if(sysstr =="Windows"):
                        fullpath.replace('\/', '\\')
                    elif(sysstr == "Linux"):
                        fullpath.replace('\\', '\/')
                    else:
                        print ("Other System tasks")
                    all_results.append(fullpath)
        elif os.path.isfile(target):
            all_results.append(target)
        else:
            print "%s is a special file (socket, FIFO, device file), pass it..." % target
    for result in all_results:
        format_single_html_prettify(result)

def format_html_prettify_parser(subparsers):
    """Argument parser for format-html-prettify command.

    format-html-prettify [dir1] [dir2] ... [dirn]
    """

    description = """
    format html file.
    """
    parser = subparsers.add_parser(
        'format-html-prettify',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('targets', nargs='*', help="Directory or HTML file")
    parser.set_defaults(func=format_html_prettify)
    return parser

def load_translated_po(arguments):
    msgs = []
    for target in arguments.pofiles:
        if os.path.isfile(target):
            msglist = load_translated_po_to_list(target)
            msgs = msgs + msglist
    for msg in msgs:
        #print msg
        s = json.loads(msg)
        print('============================Translated==============================')
        if s['msgstr'].strip():
            # print msgstr is not empty
            print(s['msgid'], s['msgstr'])
        print('==========================Not Translated============================')
        if not s['msgstr'].strip():
            # print msgstr is empty
            print(s['msgid'], s['msgstr'])

def load_translated_po_parser(subparsers):
    """Argument parser for load-translated-po command.

    load-translated-po [file1] [file2] ... [filen]
    """

    description = """
    Load the translated po file and extract msgid and msgstr.
    """
    parser = subparsers.add_parser(
        'load-translated-po',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('pofiles', nargs='*', help="PO file")
    parser.set_defaults(func=load_translated_po)
    return parser

def update_po_from_pot(arguments):
    #os.remove('translate-update.po')
    msgs = []
    for target in arguments.potfiles:
        if os.path.isfile(target):
            msglist = load_translated_po_to_list(target)
            msgs = msgs + msglist

    pomsgs = load_translated_po_to_list("translate.po")
    for msg in msgs:
        s = json.loads(msg)
        msgstr = s['msgstr']
        for pomsg in pomsgs:
            pos = json.loads(pomsg)
            if pos['msgstr'].strip() and s['msgid'] == pos['msgid']:
                msgstr = pos['msgstr']
                print('Found it [%s]'%s['msgid'])
                break
        # generate translate po
        file = open('translate-update.po', 'a')
        try:
            file.write('msgid "%s"\n' % s['msgid'])
            file.write('msgstr "%s"\n' % msgstr.encode("utf-8"))
            file.write('\n')
        finally:
            file.close()

def update_po_from_pot_parser(subparsers):
    """Argument parser for update-po-from-pot command.

    update-po-from-pot [file1] [file2] ... [filen]
    """

    description = """
    Load the translated po file and extract msgid and msgstr.
    """
    parser = subparsers.add_parser(
        'update-po-from-pot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('potfiles', nargs='*', help="POT file")
    parser.set_defaults(func=update_po_from_pot)
    return parser

def translate_pot_to_po(arguments):
    #os.remove('translate.po')
    msgs = []
    for target in arguments.potfiles:
        if os.path.isfile(target):
            msglist = load_translated_po_to_list(target)
            msgs = msgs + msglist
    newmsgs = []
    # remove dup msgid
    for msg1 in msgs:
        if msg1 not in newmsgs:
            newmsgs.append(msg1)

    for msg in newmsgs:
        # generate translate po
        file = open('translate.po', 'a')
        try:
            s = json.loads(msg)
            file.write('msgid "%s"\n' % s['msgid'])
            file.write('msgstr "%s"\n' % s['msgstr'].encode("utf-8"))
            file.write('\n')
        finally:
            file.close()

def translate_pot_to_po_parser(subparsers):
    """Argument parser for translate-pot-to-po command.

    translate-pot-to-po [file1] [file2] ... [filen]
    """

    description = """
    Load the translated po file and extract msgid and msgstr.
    """
    parser = subparsers.add_parser(
        'translate-pot-to-po',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('potfiles', nargs='*', help="POT file")
    parser.set_defaults(func=translate_pot_to_po)
    return parser

def find_untranslated_to_pot(arguments):
    parser = xml.sax.make_parser(['expat'])
    # disable external validation to make it work without network access
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)

    if arguments.silent:
        pass
    elif arguments.nosummary:
        pass

    all_results = []
    for target in arguments.targets:
        if os.path.isdir(target):
            walk_results = os.walk(target)
            for p,d,files in walk_results:
                for f in files:
                    fullpath = os.path.join(p,f)
                    sysstr = platform.system()
                    if(sysstr =="Windows"):
                        fullpath.replace('\/', '\\')
                    elif(sysstr == "Linux"):
                        fullpath.replace('\\', '\/')
                    else:
                        print ("Other System tasks")
                    all_results.append(fullpath)
        elif os.path.isfile(target):
            all_results.append(target)
        else:
            print "%s is a special file (socket, FIFO, device file), pass it..." % target

    for result in all_results:
        print(result)
        cmd = 'i18ndude find-untranslated ' + result
        print(cmd)
        os.system(cmd)
        #status, output = commands.getstatusoutput(cmd)
        #if 0 != status:
        #    print(output)

def find_untranslated_to_pot_parser(subparsers):
    """Argument parser for find-untranslated command.

    find-untranslated-to-pot [-s|-n] [dir1] [dir2] ... [dirn]
    """

    description = """
    Provide a list of ZPT files or directorys and I will output a report of places
    where I suspect untranslated messages, and write them to untranslated.pot,
    i.e. tags for which "i18n:translate" or "i18n:attributes" are missing.

    If you provide the -s option, the report will only contain a summary
    of errors and warnings for each file (or no output if there are no
    errors or warnings). If you provide the -n option, the report will
    contain only the errors for each file.
    """
    parser = subparsers.add_parser(
        'find-untranslated-to-pot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description
    )
    parser.add_argument('-s', '--silent', action='store_true', help=(
        "The report will only contain a summary of errors and warnings for "
        "each file (or no output if there are no errors or warnings)."))
    parser.add_argument('-n', '--nosummary', action='store_true', help=(
        "The report will contain only the errors for each file."))
    parser.add_argument('targets', nargs='*', help="ZPT targets")
    parser.set_defaults(func=find_untranslated_to_pot)
    return parser

def main():
    description = """
    find_untranslated_to_pot performs tasks related to i18n.

    Call find_untranslated_to_pot with one of the listed subcommands followed by
    --help to get help for that subcommand.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))
    subparsers = parser.add_subparsers(title='subcommands')
    # Add subparsers.
    find_untranslated_to_pot_parser(subparsers)
    translate_pot_to_po_parser(subparsers)
    update_po_from_pot_parser(subparsers)
    load_translated_po_parser(subparsers)
    format_html_prettify_parser(subparsers)
    translate_html_from_po_parser(subparsers)
    # Parse the arguments.
    arguments = parser.parse_args(sys.argv[1:])

    # Call the function of the chosen command with the arguments.
    errors = arguments.func(arguments)
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()