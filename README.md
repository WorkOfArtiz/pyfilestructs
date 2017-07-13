# pyfilestructs

Wrappers for essential datastructures automagically backed up in memory.

For now, I only implemented the FileDict. 
If this idea is worthwhile, it could be expanded to a more generic container.

## FileDict

A dictionairy object automatically syncronised to a file.

Example:
```
from filestructs import FileDict
from datetime    import datetime

with FileDict('program_data.pickle') as program_data:
    program_data['last used'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

```

### Behaviour non-existing files

If a file does **not** yet exist, it will create the path to the file if it doesn't exist.
The file itself however may not be created directly. (only guaranteed after close or time-event)

### Behaviour existing files

If a file does exist, it will read it in and use that data.

### Time-based behaviour

The constructor of the FileDict has a `save_every` attribute. This can be used
to save the dictionairy every n-seconds. Since it uses `time` you can use a float
to represent the number of seconds more precisely.

Example:
```
from filestructs import FileDict

with FileDict('program_data.pickle', save_every=3) as program_data:
    program_data['important data'] = "very important"
    time.sleep(120) # will have been saved while it sleeps
    crash_computer()
```

### Serialising / Deserialising

You may want to use a different serialisation method than pickle.
To accommodate for this there are the `serialiser` and `deserialiser` arguments to the constructor. (default to `pickle.dump`, `pickle.load`)


Do note that the time-based behaviours are done via seperate thread,
so errors/exceptions might not be propagated.

**Example:**
```
from filestructs import FileDict

with FileDict('program_data.json', serialiser=json.dump, deserialiser=json.load, save_every=3) as program_data:
    program_data['important data'] = "very important"
    time.sleep(120) # will have been saved while it sleeps
    crash_computer()
```