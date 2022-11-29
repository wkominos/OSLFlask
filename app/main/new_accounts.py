import csv
import xml.etree.ElementTree as ET
from app import db
from app.models import LibraryUser

def process_CSV_with_header_into_array(filePath):
    result = []

    with open(filePath, "r", encoding="utf-8-sig", newline='') as csv_file:
        parsed_csv = csv.reader(csv_file)

        for line in parsed_csv:
            result.append(line)
    return result

def parse_XML_report(report):
    tree = ET.parse(report)
    return tree.getroot()

def get_workflows_users_from_xml(xml_data):
    return xml_data.findall('user')

#these are methods
def update_library_user(user):
    pass

def add_library_user(user):
    pass



#this one I think I need to change to engage with the database
#put all the fields that are common to users in database,
#then in this function I would get all users from database
#and add all the other junk then format it. 
#remember that I need the header from the old accounts file
def build_ILL_user(newMember):
    UserName = newMember.find(".//").text
    UserValidationType = "Load"
    LastName = newMember.find(".//name/lastName").text
    PerferredName = newMember.find(".//name/preferredName")
    FirstName = PerferredName.text if PerferredName != None else newMember.find(".//name/firstName").text
    SSN = ""
    Status = "State Emp Reg"
    EMailAddress = newMember.find(".//address/[@name='1']/entry/[@name='Email']").text
    #if Phone good, if not "n/a"
    phn = newMember.find(".//address/[@name='1']/entry/[@name='Work phone']")
    Phone = phn.text.replace(",","") if phn != None else "n/a"
    MobilePhone = ""
    Department = newMember.find(".//userCategory4").text
    NVTGC = "ILL"
    Password = ""
    NotificationMethod = "Electronic"
    DeliveryMethod = "Mail to Address"
    LoanDeliveryMethod = "Mail to Address"
    AuthorizedUsers = ""
    Web = "Yes"
    agency = newMember.findall(".//extendedInfo/entry/[@name='Note']")
    #gotta find the text that starts with agency
    Address = "n/a"
    for section in agency:
        if section.text.startswith("Agency:"):
            Address = section.text.replace("Agency: ", "")
    street = newMember.find(".//address/[@name='1']/entry/[@name='Street']")
    #write a lil function for this since I keep having to validate
    Address1 = street.text if street != None else ""
    Address2 = Address1.replace(",","").strip()
    citystate = newMember.find(".//address/[@name='1']/entry/[@name='City, state']")
    st = citystate.text.split(',') if citystate != None else ""
    City = st[0].strip() if citystate != None else ""
    State = st[1].strip() if len(st) > 1 else ""
    zipcode = newMember.find(".//address/[@name='1']/entry/[@name='Zip']")
    Zip = zipcode.text if zipcode != None else "n/a"
    Site = ""
    Number = ""
    Organization = ""
    Fax = ""
    ArticleBillingCategory = ""
    LoanBillingCategory = "Default"
    Country = ""
    SAddress = ""
    SAddress2 = ""
    SCity = ""
    SState = ""
    SZip = ""
    PasswordHint = ""
    SCountry = ""
    Blocked = ""
    PlainTextPassword = ""
    UserRequestLimit = ""
    UserInfo1 = ""
    UserInfo2 = ""
    UserInfo3 = ""
    UserInfo4 = ""
    UserInfo5 = ""

    memberFullArray = [UserName, 
    UserValidationType,
    LastName,
    FirstName,
    SSN,
    Status,
    EMailAddress, 
    Phone,
    MobilePhone, 
    Department,
    NVTGC,
    Password,
    NotificationMethod,
    DeliveryMethod,
    LoanDeliveryMethod,
    AuthorizedUsers,
    Web,
    Address,
    Address2,
    City,
    State,
    Zip,
    Site,
    Number,
    Organization,
    Fax,
    ArticleBillingCategory,
    LoanBillingCategory,
    Country,
    SAddress,
    SAddress2,
    SCity,
    SState,
    SZip,
    PasswordHint,
    SCountry,
    Blocked,
    PlainTextPassword,
    UserRequestLimit,
    UserInfo1,
    UserInfo2,
    UserInfo3,
    UserInfo4,
    UserInfo5]

    return memberFullArray

def build_data_for_textfile(users):
    membersArray = []
    for user in users:
        membersArray.append(build_ILL_user(user))
    return membersArray

def convert_data_to_texfile_for_ILL(membersArray, oldUserAccts, filename):
    name = f"uploads/validation_files/{filename.split('.')[0]}-UserValidation.txt"
    line = 'separator=,\n'
    with open(name, "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        file.write(line)
        #just need the header from the oldUserAccts
        writer.writerows([oldUserAccts[0]] + membersArray)

def get_new_ILL_filename(filename):
    #get path as a variable
    name = f"../uploads/validation_files/{filename.split('.')[0]}-UserValidation.txt"
    return name

def old_data(oldUserAccts):
    oldAccts = oldUserAccts[1:]
    return oldAccts

def get_db_user_from_submitted_file(user):
    #return a dictionary?
    user_id = user.find(".//").text
    first_name = user.find(".//name/firstName").text
    last_name = user.find(".//name/lastName").text
    preferred_name = user.find(".//name/preferredName").text
    email_address = user.find(".//address/[@name='1']/entry/[@name='Email']").text
    phn = user.find(".//address/[@name='1']/entry/[@name='Work phone']")       
    phone = phn.text.replace(",","") if phn != None else "n/a"
    first_address = str(user.find(".//address/[@name='1']"))
    second_address = str(user.find(".//address/[@name='2']"))
    agency_code = user.find(".//userCategory4").text
    date_created = user.find(".//dateUserCreated").text 
    date_of_birth = user.find(".//dateOfBirth").text
    extended_info = user.find(".//extendedInfo").find('entry').text
    
    return {'user_id':user_id, 'first_name':first_name, 'last_name':last_name,
    'preferred_name':preferred_name, 'email_address':email_address, 'phone':phone,
    'first_address':first_address, 'second_address':second_address,
    'agency_code':agency_code, 'date_created':date_created, 
    'date_of_birth':date_of_birth, 'extended_info':extended_info}

#separated these two incase the structure of the file changes
def add_db_user(dictionary):
    user = LibraryUser(user_id=dictionary['user_id'], first_name=dictionary['first_name'],
    last_name=dictionary['last_name'], preferred_name=dictionary['preferred_name'], 
    email_address=dictionary['email_address'], phone=dictionary['phone'],
    first_address=dictionary['first_address'], second_address=dictionary['second_address'],
    agency_code=dictionary['agency_code'], date_created=dictionary['date_created'], 
    date_of_birth=dictionary['date_of_birth'], extended_info=dictionary['extended_info'])
    print(user)
    db.session.add(user)
    print(f'added {user}')