#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  arfedora-powerline-installer.py
#  
#  Copyright 2017 youcef sourani <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import os
import shutil
import pwd
import subprocess
import time

home         = pwd.getpwuid(os.geteuid()).pw_dir
fonts_git    = os.path.join(home,"fonts_git")
fonts_config = os.path.join(home,".config/fontconfig/conf.d")
fonts        = os.path.join(home,".local/share/fonts")

os.makedirs(fonts_git,exist_ok=True)
os.makedirs(fonts_config,exist_ok=True)
os.makedirs(fonts,exist_ok=True)

to_write = "dnf copr enable eclipseo/powerline-go -y\ndnf install powerline-go -y --best"
install_file = os.path.join("/tmp","POWERLINEINSTALL"+time.asctime().replace(":","").replace(" ","")+".sh")

bash = """# powerline-go
function _update_ps1() {
    PS1="$(/usr/bin/powerline-go -error $? -mode compatible)"
}

if [ "$TERM" != "linux" ]; then
    PROMPT_COMMAND="_update_ps1; $PROMPT_COMMAND"
fi
# powerline-go
"""


zsh = """# powerline-go
function powerline_precmd() {
    PS1="$(/usr/bin/powerline-go -error $? -shell zsh -mode compatible)"
}

function install_powerline_precmd() {
  for s in "${precmd_functions[@]}"; do
    if [ "$s" = "powerline_precmd" ]; then
      return
    fi
  done
  precmd_functions+=(powerline_precmd)
}

if [ "$TERM" != "linux" ]; then
    install_powerline_precmd
fi
# powerline-go
"""

fish = """# powerline-go
function fish_prompt
    /usr/bin/powerline-go -error $status -shell bare -mode compatible
end
# powerline-go
"""

shell = {"bash" : [ os.path.join(home,".bashrc") , "function _update_ps1()", bash] ,
		 "zsh"  : [ os.path.join(home,".zshrc") , "function powerline_precmd()", zsh] ,
		 "fish" : [ os.path.join(home,".config/fish/config.fish") , "function fish_prompt", fish]
		 }
		 
def isconfigexists(configfile,check):
	with open(configfile) as configf:
		for line in configf:
			if line.strip().startswith(check):
				return True
	return False
	
def write_config(fileconfig,shellconfig):
	with open(fileconfig,"a") as configf:
		configf.write(shellconfig)
	subprocess.call("source {}".format(fileconfig),shell=True)

def shell_config():
	for k,v in shell.items():
		if k=="fish":
			if not os.path.isfile(v[0]):
				with open(v[0],"w") as mfile:
					pass
		if os.path.isfile(v[0]):
			if not isconfigexists(v[0],v[1]):
				write_config(v[0],v[2])
	
					
def install_powerlinego():
	check = subprocess.call("rpm -q powerline-go",shell=True)
	if check!=0:
		try:
			with open(install_file,"w") as installfile:
				installfile.write(to_write)
		except:
			exit("Install PowerLine Go Fail.")
		
		check = subprocess.call("chmod 755 {}".format(install_file),shell=True)
		if check!=0:
			exit("Install PowerLine Go Fail.")
			
		check = subprocess.call("pkexec bash -e  {}".format(install_file),shell=True)
		if check!=0:
			exit("Install PowerLine Go Fail.")
			
	return True
		
def install_git():
	check = subprocess.call("rpm -q git",shell=True)
	if check!=0:
		try:
			with open(install_file,"w") as installfile:
				installfile.write("dnf install git -y --best")
		except:
			exit("Install git  Fail.")
		
		check = subprocess.call("chmod 755 {}".format(install_file),shell=True)
		if check!=0:
			exit("Install git Go Fail.")
			
		check = subprocess.call("pkexec bash -e {}".format(install_file),shell=True)
		if check!=0:
			exit("Install git Go Fail.")
			
	return True
	
def clone_powerlinefonts():
	if not os.path.isdir(os.path.join(fonts_git,"fonts")):
		check = subprocess.call("git  -C {} clone https://github.com/powerline/fonts.git --depth=1".format(fonts_git),shell=True)
		if check!=0:
			exit("Install PowerLine Fonts Fail.")
	
	
	
def cp_all_fonts_file(path,target):
	try:
		for dirname,dirs,files in os.walk(path):
			for file_ in files:
				f = os.path.join(dirname,file_)
				if os.path.isfile(f):
					if f.endswith(".ttf") or f.endswith(".otf"):
						shutil.copyfile(f,os.path.join(target,os.path.basename(f)))
	except:
		return False
	return True
	
def config_fonts():
	try:
		for dirname,dirs,files in os.walk(os.path.join(fonts_git,"fonts","fontconfig")):
			for file_ in files:
				f = os.path.join(dirname,file_)
				shutil.copyfile(f,os.path.join(fonts_config,os.path.basename(f)))
	except:
		exit("Config Fonts Fails.")
		
	check = subprocess.call("fc-cache -vf",shell=True)
	if check!=0:
		exit("Config Fonts Fails.")
		
		
if __name__ == "__main__":
	if os.getuid()==0:
		exit("Run Script Without Root Permissions.")
	install_git()
	install_powerlinego()
	clone_powerlinefonts()
	cp_all_fonts_file(fonts_git,fonts)
	config_fonts()
	shell_config()
	print("\nDone.")
