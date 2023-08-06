[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# PyJsonConfig - pyjsoncfg

Configure your Python Application with a JSON config file.
Create a sanitized sample JSON for git and demo purposes using your real config as template.


## Platform

Tested on Python3


## Development status

Beta state. The API or logical call flow might change without prior notice.

# What's new ?

Check
[`CHANGELOG`](https://github.com/kr-g/pyjsoncfg/blob/master/CHANGELOG.md)
for latest ongoing, or upcoming news


## Configuration

The environment variable `PYJSONCONFIG_BASE` (default: `"."`) is used to find the configuration file.


## Run as main

Run `pyjsoncfg` from cmd-line to create a sanitized config file using your real configuration as template.

pyjsoncfg checks for keywords like `"user", "pass", "url", "host", "remote", "port"`.
The corresponding values are replaced by dummy values. 
Keywords containing `"default"` as part of their keyword are __not__ replaced by a dummy value.
Use parameter `-k you_secret_key1` `-k you_secret_key2`... to add additional keywords to scan and replace for.

    python3 -m pyjsoncfg -f sample_cfg.json -k secret 

use redirect to create template file rather then output to stdout

    python3 -m pyjsoncfg -f sample_cfg.json -k secret > sanitized_sample_cfg.json

A sanitized sample can be found here [sanitized_sample_cfg.json](https://github.com/kr-g/pyjsoncfg/blob/master/pyjsoncfg/sanitized_sample_cfg.json)

By running `pyjsoncfg` the environment variable `PYJSONCONFIG_BASE` defaults to `"~"`


## cmd-line options

run `python3 -m pyjsoncfg -h` to see all options.


    usage: pyjsoncfg [options]

    sanitize json config file, details refer to https://github.com/kr-g/pyjsoncfg

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show version info and exit
      -d, --debug           show debug info
      -f CONFIG             input json config file (default: cfg.json)
      -l, --list            list config, do not sanitize (default: False)
      -k KEYWORD, -key KEYWORD, -keyword KEYWORD
                            additional keyword to scan for (default: [])


## Use within own code

In order to use a global configuration root set the environment before, or do by CODE (see full sample at the end)

    PYJSONCONFIG_BASE="~" python3 -m your_application 


## Config key navigation and selection

See also [`sample_cfg.json`](https://github.com/kr-g/pyjsoncfg/blob/master/pyjsoncfg/sample_cfg.json) in the github repo for the json config structure


### dict style

    # property dc is in the config file
    v = cfg()["dummy_complex"]["d"]["dc"]
    print(v,type(v))

### string selector

    # property de is new here!
    v = cfg.val( ["dummy_complex","d","de"], defval=False ) # with default value
    print(v,type(v))

### property string selector

    # property de is not new here, no chamge since created above
    v = cfg.val( cfg("dummy_complex.d.de"), defval=True ) # with default value, 
    print(v,type(v))

### namespace selector

After loading with `auto_conv=True` or calling `cfg.conv()` namespace selector is available

    v = cfg().dummy_complex.d.de
    print(v,type(v))

### setting defaults

    # also complex types are handled and resolved to namespace
    cfg.data.setdefault("a",1)
    cfg.data.setdefault("b",[2])
    cfg.data.setdefault("c",[{"e":3}])
    cfg.data.setdefault("d", [{"e": 3, "f": 4, "g": {"h": 7}}])
    cfg.data.setdefault(
        "e", [{"e": 3, "f": 4, "g": {"h": 7, "i": [1, 2, 3, 4], "j": {"z": "zoo"}}}]
    )

    # cfg().c[0].e returns 3
    # cfg().d[0].g.h returns 7
    # cfg().e[0].g.j.z returns 'zoo'


### dict handling

    cfg()["z"] = { "a": 1 }    
    cfg()["zx"] = { "a" : 1, "b" : { "c" : 2 }}
    
    cfg().zx.b.update({ "c": 3, "d": 4, "e" : 5 })

    del cfg().zx.b.c
    
    print( cfg().zx.b.items() ) 
    print( type( cfg().zx.b ) )
    print( type( cfg().zx.b.items() ) )
    
    # iterate
    for k,v in cfg().zx.b.items():
        print(k,v)

    print( type( cfg().zx.b.e ) )
    
### expand vars

with `expandvars()` all vars such as `${user}` or `${host.remote_ip}` inside an eval_string can be replaced by config values.
the default recursion level is `recursion_level=3`. change if the config file has a deeper nesting of vars.
See also [`sample_cfg.json`](https://github.com/kr-g/pyjsoncfg/blob/master/pyjsoncfg/sample_cfg.json) for the structure.

    # print structure of substsample config setting
    print( "subst var sample:", cfg().substsample )
    # subst all vars in substsample setting within a single call
    print( "result:", cfg.expand( cfg().substsample ) )
    
    # or more complicated...
    # get all vars in the string as tupel
    vars = cfg.getexpandvars( cfg().substsample ) # `eval_str` is populated with config value for substsample setting
    print( "vars:", vars )
    # get all vars and values as tupel
    exvars = cfg.expandvars( vars ) 
    print( "expandvars", exvars )
    # if required manipulate expandvars beforehand
    print( "result:", cfg.expand( cfg().substsample, expandvars=exvars ) )

    # nested or referencing vars
    print( "referencing:", cfg().substsample2 ) 
    print( "result referencing:", cfg.expand( cfg().substsample2 ) )

    # nested or referencing vars with endless loop due to self-referencing
    # stops at `recursion_level=3`
    print( "self-referencing:", cfg().substsample3 ) 
    print( "result self-referencing:", cfg.expand( cfg().substsample3 ) )
  
#### limitation of `expandvars()`
  
substitution of `dict` or complex json object is not supported.
extra whitespace within a variable specifier is not supported.

ok:

    ${user}
    ${host.remote_ip}
    
not ok:

    ${user } # tailing blank
    ${ user } # leading and tailing blank
    ${host . remote_ip} # extra white space


## Code

    import os, sys
    from pyjsoncfg import Config

    cfg = Config(
            fnam="sample_cfg.py", # file name of json config, defaults to cfg.json
            basepath=".", # base path, defaults to environment variable `PYJSONCONFIG_BASE` if not set
            not_exist_ok=True, # do not raise an error if config file is not exsting 
            auto_conv=True # after loading convert json to namespace, if false dict is used for storing
            )

    # see sample_cfg.py in github project

    val_a = cfg().dummy_complex.a 
    cfg().dummy_complex.a += 1
    val_a_after = cfg().dummy_complex.a 
    print( "a before", val_a, "after", val_a_after )

    val_array = []
    val_array.extend( cfg().dummy_array )
    cfg().dummy_array.append(17)
    val_array_after = cfg().dummy_array
    print( "array before", val_array, "after", val_array_after )

    # access functions
    #
    # val, returns the value as in the json
    # bool, converts to bool
    # int, converts to int
    # float, converts to float
    # str, converts to str

    print( bool(cfg()["dummy_complex"]["d"]["dc"] )) # get the value as given in json
    print( cfg.bool(["dummy_complex","d","dc"] )) # get interpreted as bool
    print( cfg.bool( cfg("dummy_complex.d.dc") )) # get interpreted as bool

    print( cfg.val( cfg("dummy_complex.d.dc") )) # get plain using selector
    print( cfg().dummy_complex.d.dc ) # get plain using namespace

    # save to disk
    cfg.save()

    # print to stdout
    cfg.savefd(sys.stdout)


