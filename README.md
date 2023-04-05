<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT INFO -->
<div align="center">
<h3 align="center">Job application tracker</h3>
  <p align="center">
    Bash script to update your job application status!
    <br />
    <a href="https://github.com/alexvishnevskiy/job-application-tracker/issues">Report Bug</a>
    ·
    <a href="https://github.com/alexvishnevskiy/job-application-tracker/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

The purpose of this project is to automate the process of tracking the status of job applications. The project uses the Gmail API to fetch emails related to job applications, the Google Sheets API to store information about the job applications, and ChatGPT to extract information from the emails and update the status in the Google Sheet.

The project has three main components:

**Email Retrieval**: The Gmail API is used to fetch emails related to job applications. The emails are then parsed to extract important information, such as the company name, job title, and application status.

**Information Storage**: The extracted information is then stored in a Google Sheet. The Google Sheets API is used to create a new row for each job application and populate it with the extracted information.

**Status Update**: ChatGPT is used to periodically check the status of the job application by analyzing the email content. If the status has changed, ChatGPT updates the corresponding row in the Google Sheet with the new status.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how to set up this project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

You should have **python3.8**, **google developer account**, **OpenAI developer account**.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/alexvishnevskiy/job-application-tracker.git
   ```
2. Get API Key at [https://platform.openai.com/](https://platform.openai.com/)
3. Create **.env** file in the root folder of the project and put API key from the first step into it. Like this: **OPENAI_API_KEY**="value".
4. Create a new project in the Google Developer Console, enable the Gmail API and Google Sheets API, create API credentials and download JSON file containing credentials.
5. Put JSON credentials file in the root folder, rename it to **credentials.json**.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

If you want to run interactively.
```sh
./run_script.sh start_date end_date --unread
```

If you want to run in the backgroung.
```sh
nohup ./run_script.sh start_date end_date --unread &
```

**start_date** - the start date of mail parsing in the format %Y/%m/%d, **end_date** - the end date of mail parsing in the format %Y/%m/%d, **unread** - whether to parse unread mails or not.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE.txt -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/alexvishnevskiy/job-application-tracker.svg?style=for-the-badge
[contributors-url]: https://github.com/alexvishnevskiy/job-application-tracker/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/alexvishnevskiy/job-application-tracker.svg?style=for-the-badge
[forks-url]: https://github.com/alexvishnevskiy/job-application-tracker/network/members
[stars-shield]: https://img.shields.io/github/stars/alexvishnevskiy/job-application-tracker.svg?style=for-the-badge
[stars-url]: https://github.com/alexvishnevskiy/job-application-tracker/stargazers
[issues-shield]: https://img.shields.io/github/issues/alexvishnevskiy/job-application-tracker.svg?style=for-the-badge
[issues-url]: https://github.com/alexvishnevskiy/job-application-tracker/issues
[license-shield]: https://img.shields.io/github/license/alexvishnevskiy/job-application-tracker.svg?style=for-the-badge
[license-url]: https://github.com/alexvishnevskiy/job-application-tracker/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/alexandervishnevskiy