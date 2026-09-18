# Test Cases

| ID | Test | Expected result |
|---|---|---|
| T01 | Open home page | Page loads with status 200 |
| T02 | Register with valid details | Account is created |
| T03 | Register duplicate email | Error message is shown |
| T04 | Login with valid password | Dashboard opens |
| T05 | Login with wrong password | Error message is shown |
| T06 | Search projects | Matching projects are displayed |
| T07 | Add project while logged out | User is redirected to login |
| T08 | Add project with valid details | Project is saved |
| T09 | Send duplicate join request | Second request is rejected |
| T10 | Delete another user's project | Operation is rejected |
