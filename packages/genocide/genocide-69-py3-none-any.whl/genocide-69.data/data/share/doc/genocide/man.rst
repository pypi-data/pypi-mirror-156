.. _man:

.. raw:: html

    <br>

.. title:: Manual

.. raw:: html

    <center><h1><b>manual</b></h1></center>


.. raw:: html

    <br>


**NAME**

 **GENOCIDE** - Prosecutor. Court. Reconsider OTP-CR-117/19.


**SYNOPSIS**

 ::

  genocidectl <cmd> [key=value] [key==value]


**DESCRIPTION**

 **GENOCIDE** contains :ref:`correspondence <writings>` with the
 International Criminal Court, asking for arrest of the king of the 
 netherlands, for the genocide he is committing with his new treatement laws.
 Current status is an outside the jurisdiction judgement of the prosecutor 
 which requires a :ref:`reconsider <home>` to have the king actually
 arrested.


 **GENOCIDE** holds evidence that king netherlands is doing a genocide, a 
 written :ref:`response <guilty>` where king netherlands confirmed taking note
 of “what i have written”, namely :ref:`proof <evidence>` that medicine he
 uses in treatement laws like zyprexa, haldol, abilify and clozapine are poison
 that make impotent, is both physical (contracted muscles) and mental (let 
 people hallucinate) torture and kills members of the victim groups. 


 **GENOCIDE** is a solid, non hackable bot, that runs under systemd as a 
 24/7 background service starts after reboot and is intended to be programmable
 in a static, only code, no popen, no user imports and no reading modules from
 a directory, way. It can show genocide and suicide stats of king netherlands
 his genocide into a IRC channel, display rss feeds and log simple text
 messages, source is :ref:`here <source>`.

**INSTALL**

 ::

  sudo pip3 install genocide --upgrade --force-reinstall


**CONFIGURATION**


 **irc**

 ::

  sudo genocidectl cfg server=<server> channel=<channel> nick=<nick>
  
  (*) default channel/server is #genocide on localhost

 **sasl**

 ::

  sudo genocidectl pwd <nickservnick> <nickservpass>
  sudo genocidectl cfg password=<outputfrompwd>

 **users**

 ::

  sudo genocidectl cfg users=True
  sudo genocidectl met <userhost>

 **rss**

 ::

  sudo genocidectl rss <url>

 **24/7**

 ::

  sudo cp /usr/local/share/genocide/genocide.service /etc/systemd/system
  sudo systemctl enable genocide --now


**COMMANDS**

 ::

  cmd - commands
  cfg - irc configuration
  dlt - remove a user
  dpl - sets display items
  ftc - runs a fetching batch
  fnd - find objects 
  flt - list of instances registered to the bus
  log - log some text
  mdl - genocide model
  met - add a user
  mre - displays cached output, channel wise.
  nck - changes nick on irc
  now - genocide stats
  pwd - combines nickserv name/password into a sasl password
  rem - removes a rss feed
  req - request to the prosecutor
  rss - add a feed
  slg - slogan
  thr - show the running threads
  tpc - put genocide stats into topic
  trt - torture definition


**FILES**


 | ``/usr/local/share/doc/genocide/*``
 | ``/usr/local/share/genocide/genocide.service``


**AUTHOR**

 Bart Thate 

**COPYRIGHT**

 **GENOCIDE** is placed in the Public Domain. No Copyright, No License.

