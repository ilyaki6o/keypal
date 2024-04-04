# KeyPal: your friend for providing access anywhere

Goal of KeyPal is to provide easy to use, secure and accessible service for password
management in everyday life. 

## Overview
KeyPal is a telegram bot providing access to remote server
with running instance of BitWarden password manager.  
It may be inconvenient for some users to interact with BitWarden, so our
Telegram bot provides access to the most useful in every person's
routine functions for dealing with passwords of all kind.

## Features
#### Planned functionality:
- Password management
- Password generator
- Backup copy creation
- Password recovery
- Notification about spoiled passwords
#### May be implemented (or may not be)
- 2 factor authentification
- Import and export of data  
- End-to-end encryption

and more...


#### Interface (functional prototype)
The following interface functions are planned to be implemented:
- Register password with meta information (login, access rights, ...)
- Get password associated with login or id
- Delete password by id
- Generate password
- Export passwords
- Import passwords

#### Used technologies
- BitWarden api
- Something to work with Telegram api
- Some database to store users(maybe)
- Some encryption mechanism (maybe)
- Some 2 factor authentification (maybe)
