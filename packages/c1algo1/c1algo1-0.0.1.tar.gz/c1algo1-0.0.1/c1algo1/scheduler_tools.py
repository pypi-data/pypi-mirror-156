# sorts a list of courses by number of professors willing to teach them (ascending order)
def sort_courses_by_prof_interest(input_with_interested_profs, historical_year=None):

    if historical_year is None:
        # pull out the schedule as we only want to sort this key of the larger dict
        schedule = input_with_interested_profs['schedule']

        # sort each sem and then re-insert sorted sem into schedule
        for sem in schedule:
            sorted_list = sorted(schedule[sem], key=lambda x: (len(x['interestedProfs'].items()), sum(x['interestedProfs'].values())))
            schedule[sem] = sorted_list
        input_with_interested_profs['schedule'] = schedule
    else:
        # pull out the schedule as we only want to sort this key of the larger dict
        schedule = input_with_interested_profs['historicalData'][historical_year]

        # sort each sem and then re-insert sorted sem into schedule
        for sem in schedule:
            sorted_list = sorted(schedule[sem], key=lambda x: (len(x['interestedProfs'].items()), sum(x['interestedProfs'].values())))
            schedule[sem] = sorted_list
        input_with_interested_profs['historicalData'][historical_year] = schedule

    return input_with_interested_profs

# associates professors with courses that they are potentially interested in teaching
def associate_profs_with_courses(scheduler_input, historical_year=None):
   
    # extract profs
    professors = scheduler_input['professors']

    # go through and an empty interestedProfs key to each course in the schedule
    if historical_year is None:
        for current_semester in scheduler_input['schedule']:
            for course in enumerate(scheduler_input['schedule'][current_semester]):
                scheduler_input['schedule'][current_semester][course[0]]['interestedProfs'] = {}    
    
        # loop through each semester, and each course slotted to be taught that semester
        for current_semester in scheduler_input['schedule']:
            for course in scheduler_input['schedule'][current_semester]:
                # loop through each professor, and look to see what courses they are interested in teaching
                for prof in professors:
                    # check if this prof prefers not to teach this semester #TODO: this condition is very strict like this, should be a preference? 
                    #if current_semester == prof['preferredNonTeachingSemester'].lower():
                    #    continue
                    course_preferences = prof['coursePreferences']
                    for interested_course in course_preferences:
                        #TODO: check the prof can teach for this semester before we add them to the interested list!
                        code = interested_course['courseCode'].replace(" ", "")
                        score = interested_course['enthusiasmScore']
                        if score > 0:
                            # check if this course exists in courses, if not, move on
                            search = next((i for i, offered_course in enumerate(scheduler_input['schedule'][current_semester]) if offered_course['course']['code'] == code), None)
                            if search == None:
                                #scheduler_input['schedule'][current_semester][search]['interestedProfs'] = {}
                                #print('course ID {} does not exist in provided {} input check again'.format(code, current_semester))
                                continue
                            # see if a 'interestedProfs' key has been inserted into dict yet, if not, create it, otherwise update it.
                            # NOTE: this is a temporary key we are manually inserting into each CourseOffering in the schedule, it can be removed. its for our uses.
                            try:
                                scheduler_input['schedule'][current_semester][search]['interestedProfs'][prof['id']] = interested_course['enthusiasmScore']
                            except KeyError as e:
                                scheduler_input['schedule'][current_semester][search]['interestedProfs'] = {prof['id']: interested_course['enthusiasmScore']}
    else:
        for current_semester in scheduler_input['historicalData'][historical_year]:
            for course in enumerate(scheduler_input['historicalData'][historical_year][current_semester]):
                scheduler_input['historicalData'][historical_year][current_semester][course[0]]['interestedProfs'] = {}

        # loop through each semester, and each course slotted to be taught that semester
        for current_semester in scheduler_input['historicalData'][historical_year]:
            for course in scheduler_input['historicalData'][historical_year][current_semester]:
                # loop through each professor, and look to see what courses they are interested in teaching
                for prof in professors:
                    # check if this prof prefers not to teach this semester #TODO: this condition is very strict like this, should be a preference? 
                    #if current_semester == prof['preferredNonTeachingSemester'].lower():
                    #    continue
                    course_preferences = prof['coursePreferences']
                    for interested_course in course_preferences:
                        #TODO: check the prof can teach for this semester before we add them to the interested list!
                        code = interested_course['courseCode'].replace(" ", "")
                        score = interested_course['enthusiasmScore']
                        if score > 0:
                            # check if this course exists in courses, if not, move on
                            search = next((i for i, offered_course in enumerate(scheduler_input['historicalData'][historical_year][current_semester]) if offered_course['course']['code'] == code), None)
                            if search == None:
                                #scheduler_input['schedule'][current_semester][search]['interestedProfs'] = {}
                                #print('course ID {} does not exist in provided {} input check again'.format(code, current_semester))
                                continue
                            # see if a 'interestedProfs' key has been inserted into dict yet, if not, create it, otherwise update it.
                            # NOTE: this is a temporary key we are manually inserting into each CourseOffering in the schedule, it can be removed. its for our uses.
                            try:
                                scheduler_input['historicalData'][historical_year][current_semester][search]['interestedProfs'][prof['id']] = interested_course['enthusiasmScore']
                            except KeyError as e:
                                scheduler_input['historicalData'][historical_year][current_semester][search]['interestedProfs'] = {prof['id']: interested_course['enthusiasmScore']}
                            
    return scheduler_input
