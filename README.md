# ekiefl.github.io

This is the source code for https://ekiefl.github.io/.

# Developer instructions

Install ruby 3.2.2 and specify it locally:

```bash
rbenv install 3.2.2
rbenv local 3.2.2
```

Now install bundler

```
gem install bundler
```

Install all the gems in the `Gemfile`:

```
bundle install
```

And run the following command in this directory:

```
bundle exec jekyll serve --incremental
```

You should see a similar output in your terminal:

```
Configuration file: /Users/evan/Software/web/_config.yml
Configuration file: /Users/evan/Software/web/_config.yml
            Source: /Users/evan/Software/web
       Destination: /Users/evan/Software/web/_site
 Incremental build: enabled
      Generating...
                    done in 6.585 seconds.
 Auto-regeneration: enabled for '/Users/evan/Software/web'
Configuration file: /Users/evan/Software/web/_config.yml
    Server address: http://127.0.0.1:4000/
  Server running... press ctrl-c to stop.
```

This basically runs a local server for you to see the changes you've made locally. You can access to this server by visiting the URL `http://127.0.0.1:4000/` with your browser.

With the `--incremental` flag every change you will make in any of the files will be reflected to your local website automatically.

If you are not seeing some of the changes you expect to see, press `ctrl-c` to stop the server on your termianl, clean out the static web directory by running the command `rm -rf _site/`, and re-run the server using the command above.

# Notes

If you want to show/hide content, you can use this notation in your markdown files:

```
<details markdown="1"><summary>Show/Hide SOME CONTENT</summary>

SOME CONTENT GOES HERE

</details>
```

If you want to show summary sections with a different background color, you can use this notation:

```
<div class="extra-info" markdown="1">

<span class="extra-info-header">Smart title for extra info</span>

EXTRA INFO GOES HERE

</div>
```

You should feel free to use warning and notice statements:

```
{:.warning}
A warning messages goes here.

{:.notice}
A notice statement goes here.
```
