# Getting started

## Overview

{% hint style="info" %}
Before beginning, [contact our customer success team](https://www.launchableinc.com/contact-for-poc) to initiate an enterprise proof of concept (POC), or [sign up](https://app.launchableinc.com/signup) directly from our website. (Launchable is free for open source projects.)
{% endhint %}

{% hint style="info" %}
If you use pytest or nosetests, you don't need to use the Launchable CLI! We offer native plugins for those test runners. Check out the [pytest](../resources/integrations/pytest.md) and [nose](../resources/integrations/nose.md) pages for more info.
{% endhint %}

The Launchable CLI connects your CI pipeline with Launchable. To get started,

1. install the CLI as part of your CI script,
2. set your Launchable API key, and
3. verify connectivity

Then follow the instructions for your test runner or build tool to [send data to Launchable](../sending-data-to-launchable/).

## Installing the CLI

The Launchable CLI is a Python3 package that you can install from [PyPI](https://pypi.org/project/launchable/).

{% hint style="warning" %}
The CLI requires both **Python 3.5+** _and_ **Java 8+**.
{% endhint %}

You can install the CLI in your CI pipeline by adding this to the part of your CI script where you install dependencies:

```bash
pip3 install --user --upgrade launchable~=1.0
```

## Setting your API key

First, create an API key for your workspace at [app.launchableinc.com](https://app.launchableinc.com). This authentication token allows the CLI to talk to Launchable.

Then, make this API key available as the `LAUNCHABLE_TOKEN` environment variable in your CI process. How you do this depends on your CI system:

| CI system              | Docs                                                                                                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure DevOps Pipelines | [Set secret variables](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops\&tabs=yaml%2Cbatch#secret-variables)                                              |
| Bitbucket Pipelines    | [Variables and secrets](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)                                                                                                   |
| CircleCI               | [Using Environment Variables](https://circleci.com/docs/2.0/env-vars/)                                                                                                                               |
| GitHub Actions         | [How to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets)                                                                                     |
| GitLab CI              | [GitLab CI/CD environment variables](https://docs.gitlab.com/ee/ci/variables/)                                                                                                                       |
| GoCD                   | [Setting variables on an environment](https://docs.gocd.org/current/faq/dev\_use\_current\_revision\_in\_build.html#setting-variables-on-an-environment)                                             |
| Jenkins                | <p><a href="https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-secure-guide/injecting-secrets">Injecting secrets into builds</a></p><p>(Create a global "secret text" to use in your job)</p> |
| Travis CI              | [Environment Variables](https://docs.travis-ci.com/user/environment-variables/)                                                                                                                      |

## Verifying connectivity

After setting your API key, you can add `launchable verify || true` to your CI script to verify connectivity. If successful, you should receive an output such as:

```bash
$ launchable verify || true

Organization: <organization name>
Workspace: <workspace name>
Platform: macOS-11.4-x86_64-i386-64bit
Python version: 3.9.5
Java command: java
launchable version: 1.22.3
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](../resources/troubleshooting.md).

{% hint style="info" %}
We recommend including `|| true` so that the exit status from the command is always `0`.
{% endhint %}

## Next steps

Now that you've added the CLI to your pipeline, you can start [sending data to Launchable](../sending-data-to-launchable/) to analyze and optimize your test runs.
