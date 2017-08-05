## Taggo

A Facebook bot full configurable over yaml.

## Cloning and Running

```

git clone https://github.com/vttach/taggo.git

# change to cloned directory
cd taggo/

# Install all the dependencies
pip install -r requirements.txt

# run the wsgi server
python -m sanic main.app

or 

# run the main script
python main.py


```

## Environmental Variables:

```sh
export YAML_URL=<url where the yaml has to be loaded from>
export ACCESS_TOKEN=<facebook page access token>
export VF_TOKEN=<verfication token for bot>
```

## Configuration

```yaml

default: 
   ....

requests:
   - ...

```

The yaml defines rule called requests which defines the set of text patterns to be matched from. And the default rule which will be executed when no match is found on requests.

A typical request command looks like below

```yaml

requests:
  - name: sayhello
    pattern: hello
    response:
       type: text
       text: hello
  
  - name: order tracking
    pattern: track\s+order\s+(?P<track>.*)?
    webhook: http://api.helloworld.com
    method: post
    type: json
    params: 
       - track
    response:
       type: template
       template_type: generic
       elements:
          - title: "title"
            image_url: "https://cldup.com/xxx.jpg"
            subtitle: "We have a subtitle"
            buttons: 
               - type: "web_url"
                 url: "https://mycompany.in"
                 title: "mycompany"
```

* **name**: Name of the action.
* **pattern**: A regex pattern to match the particular action.
* **webhook**: A webhook which can be initiated when the message is recived.
* **method**: Method assosiated with the webhook
* **params**: Parameters which will sent along the request to webhook url. Taken 
from the named groups in pattern.
* **response**: Type of response to be made by bot(defaults to text). But also
supports templates. The parameter ```template_type``` can be either **generic** or **list** template.

## License

MIT
