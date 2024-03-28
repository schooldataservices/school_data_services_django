def get_template(school, sport):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
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

            .underlined-heading h1 {{
                color: #007BFF;
                text-decoration: underline;
            }}

            .image-container {{
                display: flex;
                flex-direction: row;
                align-items: center;
                margin-top: 20px;
            }}

            .social-icons {{
                display: flex;
                flex-direction: row;
                align-items: center;
                margin-left: 10px;
            }}

            .social-icons a {{
                display: block;
                margin-top: 10px;
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
            <div class="underlined-heading">
                <h1>Looking for Baseball Jerseys & Apparel for the Upcoming Season?</h1>
            </div>

            <p>Hello {school}! </p>
            
            This is Chris with Customplanet; we are a local company that provides custom sports apparel, spirit packs, hoodies, hats, team uniforms, and much more. I wanted to drop a message to provide a local option for all of your school sports needs. 
            
            
            <p>Why choose us?</p>
            <ul>
                <li>Local Expertise in the KC area paired with Quality Customer Service</li>
                <li>Customization Options, and Superior Quality </li>
                <li>Quick Turnaround: Fast and efficient service to meet those tight schedules.</li>
                <li>Reliablity: an e-commerce website established in 2009, we have done almost 10 million in sales serving local schools and customers around the world.</li>
            </ul>
           
            <p>We offer free samples and quotes! Hope we can help you in the near future!</p>
            <p>Visit our website <a href="https://customplanet.com/">www.customplanet.com</a> or give us a call/text at <a href="(801) 810-8337" class="underline"> (801) 810-8337</a></p>

            <div class="image-container">
                <div class="social-icons">
                    <a href="https://www.customplanet.com/" target="_blank">
                        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9Jolo0qsbBbemgBEHbuhLUnXtFVxuA9FPXuZj07YnIA&s" alt="Customplanet Logo" width="80px">
                    </a>

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

            <p class="footer">Positively,<br>Your Team at Customplanet <br>{sport} season is nearly here! </br>  </p>
        
            <p class="unsubscribe-link">
                <a href="https://customplanet.com/index.php?route=common/unsubscribemail" target="_blank" class="unsubscribe-link">
                    If you wish to unsubscribe, click here.
                </a>
            </p>
        </div>
    </body>
    </html>
    '''


#ideas. 
#Reply to email, and get code for 10% off
#Send email with QR Code, scan for special offer. 
#Make the social media icons smaller