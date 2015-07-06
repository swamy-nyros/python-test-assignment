var app = angular.module('myApp', ['ngRoute']);

app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.        
        when('/main', {
            templateUrl: 'static/templates/home.html'            

        }).
        when('/signup', {
            templateUrl: 'static/templates/signup.html'            
                              
        }).
        when('/login', {
            templateUrl: 'static/templates/login.html'
                              
        }).
        when('/logout', {
            templateUrl: 'static/templates/login.html',
            
                              
        }).
        when('/message', {
        	templateUrl: 'static/templates/user_list.html'
        }).
        when('/usermessage', {
            templateUrl: 'static/templates/user_message.html'
        }).

        otherwise({
            redirectTo: '/'
        });
}]);

app.controller("MainController", function($scope, $rootScope, $http, $log, $location) {

$scope.fields = {};
$scope.alerts = '';
$scope.users = '';
$scope.messages = '';

	$scope.submitMyForm=function(){
        // /* while compiling form , angular created this object*/
        // var data=$scope.fields;  
        // console.log(data)
        // /* post to server*/
        // $http.post("/signup", data: data);    

        $http({
             method: 'POST',
             url: '/signup',
             data: { fullname: $scope.fields.name , email: $scope.fields.email , password: $scope.fields.password }
             }).
             success(function (data, status, headers, config) {
             	// $rootScope.guests = data;
             	console.log("success, need to show message and redirect to login");
             	// console.log(data[0].status_message);
             	console.log(data.status_message);
             	console.log(status);
             	$scope.alerts = data;
             	// $rootScope.guests.push(data);
      			// $rootScope.status = 'success';
      			if (data.status_message=="Error"){
             		$location.path('/signup');
             	} else {
             		$location.path('/login');
             	}
      			
              //alert("successfull");
            // $location.path('/products/'+$routeParams.id+'/upload');
             }).
             error(function (data, status, headers, config) {
             	console.log("Error, may be duplicate email");
             	console.log(data);
             	console.log(status);
             	// $rootScope.guests.push(data);
      			$rootScope.status = 'Error';
      			$location.path('/signup');
             });
        


        


             // $location.path('/signup');
        
             /*error(function (data, status, headers, config) {
             //alert("failed!");
             });*/

 /*       $http({
        	method: 'GET'
        });
*/


    
    }

    $scope.submitMyForm1=function(){
        console.log("entering to messages")
        // /* while compiling form , angular created this object*/
        // var data=$scope.fields;  
        // console.log(data)
        // /* post to server*/
        // $http.post("/signup", data: data);    

        $http({
             method: 'POST',
             url: '/usermessage',
             data: { reciver: $scope.fields.reciver,message: $scope.fields.message }
             }).
             success(function (data, status, headers, config) {
                // $rootScope.guests = data;
                console.log("success, need to Message form");
                // console.log(data[0].status_message);
                console.log(data.status_message);
                console.log(status);
                $scope.alerts = data;
                // $rootScope.guests.push(data);
                // $rootScope.status = 'success';
                if (data.status_message=="Error"){
                    $location.path('/usermessage');
                } else {
                    $location.path('/message');
                }
                
              //alert("successfull");
            // $location.path('/products/'+$routeParams.id+'/upload');
             }).
             error(function (data, status, headers, config) {
                console.log("Error, may be duplicate email");
                console.log(data);
                console.log(status);
                // $rootScope.guests.push(data);
                $rootScope.status = 'Error';
                $location.path('/usermessage');
             });
             // $location.path('/signup');
             /*error(function (data, status, headers, config) {
             //alert("failed!");
             });*/

 /*       $http({
            method: 'GET'
        });
*/


    
    }










    $scope.loginForm=function(){

    	$http({
             method: 'POST',
             url: '/login',
             data: { fullname: $scope.fields.name , password: $scope.fields.password }
             }).
             success(function (data, status, headers, config) {
             	console.log('log in success')
             	console.log(data)
                console.log(data.userlist)
                console.log(data.messagelist)
             	$scope.users = data.userlist;
                $scope.messages = data.messagelist;
             	
                $location.path('/message');
              //alert("success");
            // $location.path('/products/'+$routeParams.id+'/upload');
             }).
             error(function (data, status, headers, config) {
                console.log("anushaaaaaaaaaaaaa")
             	console.log(data)
             //alert("failed!");
             });

      /*  $http({
        	method: 'GET',
        	url: '/message',
        	data:
        });
*/


    }



    logout = function() {
        localStorageService.clearAll();
    };

  /*  $scope.logout=function(){
    $http({
        method: "GET",
        url: '/logout',
        
        }).
        success(function (data, status, headers, config) {
        
        
        $location.path('/login');
        }).
        error(function (data, status, headers, config) {
            console.log("error")
            console.log(data)
        })

    }
  */ 

/*	$http({method: 'GET', url: '/signup'})
	.success(function(data, status, header, configs) {
	// success code
	console.log('success')
	}
	.error(function(data, status, header, configs) {
	// error code
	}*/
});


/*

	$scope.signUp = function() {

  	$log.log("test");

	// get the URL from the input
	var userInput = $scope.input_url;
	var fullname = $scope.fullname;
	var email = $scope.email;
	var password = $scope.password;*/
	// fire the API request
/*	$http.post('/signup', {"fullname": fullname, "email": email, "password": password }).

	    success(function(results) {
	      $log.log(results);
    }).
    error(function(error) {
      $log.log(error);};

    });
*/
    /*$http.post("/signup", {request_name: 'Test Name', request_body: 'Test Body'});*/




	/*$scope.getData = function(){*/

		/*var fullname = $scope.fullname;
		var email = $scope.email;
		var password = $scope.password;*/

		/*$http({method: 'POST', url: '/signup'})
		.success(function(data, status){



			console.log('success')
		})
		.error(function(data, status) {
		// error code
		console.log('error')
		})*/

	/*	$http.post('/signup', {"fullname":fullname, "email":email,"password":password})
		.success(function(data, status) {
			console.log('data')
      	$log.log(getData);
    	})
    	.error(function(error) {
      	$log.log(error);
    	});
*/
		/*var name = $scope.full_name;
		var email = $scope.email;
		var pwd = $scope.pwd;
		$http.post('/signup', {"name":name, "email":email,"pwd":pwd})
		.success(function(results) {
      	$log.log(results);
    	})
    	.error(function(error) {
      	$log.log(error);
    	});
		url : "/polls/2/comment/", // the endpoint
            type : "POST", // http method
            data : { the_post : $('#post-comment').val() },

	};*/
	

/*	jQuery.post('/signup',
	{'user_name': user_name , 'email':email, 'password':password},
	function(data,textStatus, jqXHR){console.log('POST response: ');console.log(data);});


	$.ajax({
    type: 'POST',
    url: '/signup',
    data: JSON.stringify({'user_name': user_name , 'email':email, 'password':password}),
    contentType: 'application/json',
    success: function(data,textStatus, jqXHR) {
        console.log('POST response: ');
        console.log(data);
	    }
	});
*/



	

	/*$scope.signup = function(){

		$http({method: 'GET', url: 'http://localhost:8080/signup'})
		.success(function(data, status, header, configs) {
		// success code
		console.log('success')
		}
		.error(function(data, status, header, configs) {
		// error code
		console.log('error')
		}

		$http({method: 'POST' , url: 'http://localhost:8080/signup'})
		.success

	}*/
/*
	$scope.login = function(){

		$http({})


	}
*/
	



/*	$scope.signup = function() {

		if(!$scope.regForm.$invalid){
			var email = $scope.user.email;
			var password = $scope.user.password;

			if (email && password){
				auth.$createUser(email, password)
					.then (function() {
					//success
					console.log(' user successfully created ');
					$location.path('/home');

				}, function(error) {
					//failure
					console.log(error);
					$scope.regError = true;
					$scope.regErrorMessage = error.message;
				});
			}
			//console.log('Valid for submission');
		}
*/



	/*$.ajax({
				    type: 'POST',
				    url: '/signup',
				    data: JSON.stringify({'fullname': name , 'email': email, 'password':password}),
				    contentType: 'application/json',
				    success: function(data,textStatus, jqXHR) {
				        console.log('POST response: ');
	});			        console.log(data);
					    }
					});*/






