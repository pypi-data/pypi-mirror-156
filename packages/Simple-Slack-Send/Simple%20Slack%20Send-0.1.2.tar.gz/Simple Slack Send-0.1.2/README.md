Simple Slack Send - easily send slack messages in your CI pipelines
===

Simple Slack Send is designed to push templated slack notifications from you CI pipelines using Slack's incoming webhooks.

Template engine
---

Simple Slack Send uses [Jinja2](https://palletsprojects.com/p/jinja/) under the hood to produce Slack messages in JSON format. You can use any expression (values, includes, conditions, loops etc.) that is allowed by Jinja.
If the rendering engine's output is empty, no message is sent.

Parameter sources
---

Jinja templates are fed with values from multiple sources given as command arguments:

1. env files with key-value pairs ie. `-e production.env` or `--env-file=staging.env`
2. json files ie. `-j terraform-output.json` or `--env-file=infrastructure.json`
3. key-value pairs provided as command arguments ie. `-v env_name=jupiter` or `--var instance_type=small`
4. system environment - turned on/off with `--sys-env`/`--no-sys-env` option; on by default


Configuration
---

You can pass Slack's webhook url by settings `SLACK_WEBHOOK_URL` env variable or using `--webhook-url` argument.


Example usage
===

message.json.tpl:
```
{% if BITBUCKET_EXIT_CODE == "0" %}
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": ":large_green_circle: Commit {{ BITBUCKET_COMMIT }} built successfully."
      }
    }
  ]
}
{% else %}
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": ":red_circle: Commit {{ BITBUCKET_COMMIT }} failed to build. Visit <https://bitbucket.org/{{ BITBUCKET_REPO_FULL_NAME }}/pipelines/results/{{ BITBUCKET_BUILD_NUMBER }}|pipeline> for details."
      }
    }
  ]
}
{% endif %}
```

```
simple-slack-send message.json.tpl
```