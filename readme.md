# Mailchimp to TestFlight

I wanted a simple way to automatically sync Mailchimp subscribers to a TestFlight Beta list without using another third party app.

## How does it work?

Once you generate and include the APIs in this script, it will pull all emails from both services and add missing emails to TestFlight.

## Here is what you need to do

1. Generate a [Mailchimp API key.](https://mailchimp.com/help/about-api-keys/)
2. You'll also need the **Audience ID** number. You can find this under Audience/Settings/Audience name and defaults. You'll also need the Mailchimp datacenter ID. It's at the end of the API key.
3. Generate an [Apple Store Connect API key.](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api)
4. You'll need the **Issuer ID** and the **Key ID** along with the **Private_Key.p8** that you'll have to download after generating. You can only download it once so be careful. All this information should be on the same screen after generating the private key.
5. It's up to you on how to store the private key for use. You can have it in some folder with chmod 600 permissions (less secure) or set it as an environment variable (more secure). I've included both options.

## Running it

Install python, requests, and pyjwt.
Then: `python your_script_name.py`

That's it. The script should do it's magic.

## Automation tip

If you want to run this everyday on say, a raspberry pi, set a cron job to do the task.
`0 */12 * * * /path/to/your/python3 /path/to/your/script/mailchimp_to_testflight.py`
Replace /path/to/your/python3 with the path to your Python 3 interpreter (usually /usr/bin/python3), and /path/to/your/script/mailchimp_to_testflight.py with the full path to your script.
