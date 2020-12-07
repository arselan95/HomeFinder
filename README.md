# HomeFinder

### FRONTEND
- Remote working front end team.
- Used React
- Backend implemented as per frontend team requested the data.

### BACKEND
- Me and my backend team mate.
- Developed the backend application in Python using Python Flask framework
- Developed the functionality for each of the features mentioned in the functional requirements
- Created REST APIs and returning data is JSON format using the cURL links for UI integration
- Created the MySQL Database schema and responsible for handling the dataflow.
- Flask app hosted on AWS EC2
- MySQL db instance on AWS RDS
- Kanban board updated on the Project Github board


### FEATURES AND DESIGN
Backend Features implemented as per roles:<br>

<h5>Admin:</h5><br>
- Approve / Remove user <br>
- View all users<br>
- Remove any user<br>
- View Reported Listing by Buyer / Renter<br>
- Remove user based on Reported Listings<br>

<h5>Renter:</h5>
- View All Rentals<br>
- Listing Details / Submit application for that listing<br>
- inbox : view approved / rejected applications<br>
- view pending apps<br>
- Favorites : Add / Remove / View favorites<br>

<h5>Buyer / realtor: (depending who is logged in: relevant data will be displayed)</h5> <br>
- View All Sales<br>
- Listing Details / Submit application for that listing. (a gmail will be sent on localhost, smtp server)<br>
- inbox : view approved / rejected applications<br>
- view pending apps<br>
- Favorites : Add / Remove / View favorites<br>

<h5>Landlord / Realtor: (depending who is logged in: relevant data will be displayed)</h5><br>
- Create Rental Listing.<br>
- View my Rent listings.<br>
  - Update / Delete<br>
- View applications of their listings.<br> 
- approve / reject application with a note to renter<br>

<h5>Seller / Realtor: (depending who is logged in: relevant data will be displayed)</h5><br>
- Create Sale Listing.<br>
- View my Sale listings.<br>
  - Update / Delete<br>
- View applications of their listings. <br>
- approve / reject application with a note to buyer or buyer realtor.<br>


<h5>Search: (depending who is logged in: relevant data will be displayed)</h5><br>
- All can search.<br>



<h2> Design</h2>

<h3>Backend Deployed Components Diagram:</h3>

![Screenshot](BackendComponentArchitecture.png)

<h3>Database design:</h3>

<h3>Class Diagram:</h3>
<ul>
<li>
<h4> Class Diagram : Registered User </h4>
  </li>
  <br>
  

![Screenshot](homefinderClassDiagram.png)
<ul>
<li>
<h4> Class Diagram : Admin </h4>
  </li>
</ul>
<br>

![Screenshot](homefinder-AdminClassDiagram.png)

<h2> Functionalities </h2>

<h3> Use case: </h3>

![Screenshot](UsecaseDiagram.png)

<h3> Sequence: </h3>

![SequenceDiagram](SequenceDiagram.png)


<h2> Decisions Design </h2>

<h3> State design: </h3>

![StateDiagram](StateDiagram.png)

<h3> Activity Diagram: </h3>

![ActivityDiagram](ActivityDiagram.png)
