# Connecting to the Server

This file contains instructions on how to connect to the group's server.

## SSH

To connect to the server, you will need to use SSH. The server address is `sessa.ku.dk`. You will need to use your KU username and password to log in.

```bash
ssh username@sessa.ku.dk
```

## File Transfer

You can use `scp` to transfer files to and from the server.

To copy a file from your local machine to the server:

```bash
scp /path/to/local/file username@sessa.ku.dk:/path/to/remote/directory
```

To copy a file from the server to your local machine:

```bash
scp username@sessa.ku.dk:/path/to/remote/file /path/to/local/directory
```
