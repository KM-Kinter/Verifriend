Instructions for Bot Setup - User Verification

Hello Developer! Below you will find the necessary steps to set up the bot code for user verification on the Discord server "Hackerspace Trójmiasto":

1. Installing Required Libraries: Ensure that you have the necessary libraries installed. Use the following command in the terminal:

pip install discord.py

2. Setting up Bot Token and Server Information: Upon running the code, you will be prompted to provide the following details:

  Bot Token: Enter your bot token for accessing the Discord API.
  Verification Role Name: Input the name of the verification role.
  Guild ID: Enter the ID of your Discord server.
  Channel ID: Provide the ID of the channel where verification messages will be sent.
  Removal Channel ID: Enter the ID of the channel where information about removed users will be posted.

3. Customizing Bot Configuration: After entering the required information, the code will be configured accordingly.

4. Customizing Server Settings: Update the value of the variable guild_id in the code to match your Discord server's ID.

5. Customizing Verification Messages: Modify the content of the verification messages in the code section await member.send(...) to tailor them to your preferences.

6. Adjusting Timeframes: Modify the value of days_since_join in the code to change the timeframe for sending warning messages and removing unverified users.

7. Running the Bot: After making the necessary adjustments and providing the required details, execute the bot to ensure its proper functioning. Type the following command in the terminal:

python your_file_name.py

Ensure to adapt the code according to your specific requirements. If you encounter any issues or need further assistance, refer to the Discord.py documentation or reach out to the user Kinter (search by username: technologista) on Discord.
