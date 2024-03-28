def get_intro_template():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body{{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}

            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}

            h1 {{
                color: #007BFF;
            }}

            p {{
                font-size: 16px;
                line-height: 1.6;
            }}

            a, .underline:hover {{
                color: #007BFF;
                text-decoration: none;
            }}

            a:hover, .underline:hover {{
                text-decoration: underline;
            }}

            .image-container {{
                /* Images stored in the same container will be stacked vertically based on flex direction */
                /* image-container settings are dominant over social-icons*/
                display: flex;
                flex-direction: row;  /* Change this to column to stack vertically */
                align-items: center;  /* Align items to the center */
                margin-top: 20px;
            }}

            .social-icons {{
                display: flex;
                flex-direction: column; /* Stack the icons vertically */
                align-items: center;   /* Center the icons horizontally */
                margin-left: 10px;     /* Adjust as needed for spacing */
            }}

            .social-icons a {{
                display: block;
                margin-top: 10px; /* Adjust the spacing as needed */
            }}

             .unsubscribe-link {{
            font-size: 13px;
            color: #777;
            text-decoration: none;
            }}

            .unsubscribe-link:hover {{
                text-decoration: underline;
            }}

        </style>
    </head>
    <body>
        <div class="container">
            <h1>Little League Season Is Coming Fast!!</h1>
            <p>At Customplanet we can outfit your team or league head to toe. We have league and team discounts, and are ready to ship! Jerseys are only $23 with your player names and numbers on them. </p>
      
            <p>Hurry, because the Offical MLB jerseys sell out every year!</p>
            <p>Visit our website <a href="https://customplanet.com/Majestic-Jerseys.aspx">www.customplanet.com</a> or give us a call/text at <a href="(801) 810-8337" class="underline"> (801) 810-8337</a></p>


            <div class="image-container">
                <a href="https://www.customplanet.com/" target="_blank">
                    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9Jolo0qsbBbemgBEHbuhLUnXtFVxuA9FPXuZj07YnIA&s" alt="Customplanet Logo" width="100px">
                </a>

                <div class="social-icons">
                    <a href="https://twitter.com/customplanet" target="_blank">
                        <img src="https://1000logos.net/wp-content/uploads/2017/02/Twitter-Logosu.png" alt="Twitter Logo" width="95px">
                    </a>

                    <a href="https://www.facebook.com/CustomPlanetDotCom/" target="_blank">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Facebook_icon.svg/2048px-Facebook_icon.svg.png" alt="Facebook Logo" width="70px">
                    </a>

                     <a href="https://www.instagram.com/customplanetinc/" target="_blank">
                        <img src="https://cdn.mos.cms.futurecdn.net/6dDoc8GV9fYUPExgLYPqqT-1200-80.jpg" alt="Instagram Logo" width="110px">
                    </a>

                </div>

            </div>
            
            <div class="image-container" style="margin-top: 30px;">
                <a href="https://customplanet.com/Majestic-Jerseys.aspx"> 
                    <img src="https://i.imgur.com/HvkaGes.png" alt="Majestic Gear" width="600px"> 
                </a>
            </div>

             <!-- Unsubscribe link -->
            <p class="unsubscribe-link">
                <a href="https://customplanet.com/index.php?route=common/unsubscribemail" target="_blank" class="unsubscribe-link">
                    If you wish to unsubscribe, click here.
                </a>
            </p>
        </div>
    </body>
    </html>
    '''


#embed opt out link