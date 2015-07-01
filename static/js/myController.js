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
            templateUrl: '/logout'
                              
        }).
        otherwise({
            redirectTo: '/'
        });
}]);

app.controller("MainController", function($scope, $http, $log) {

	$scope.getData = function(){

	/*	$http({method: 'POST', url: 'http://localhost:8080/#/signup'})
		.success(function(data, status){


			console.log('success')
		})
		.error(function(data, status) {
		// error code
		console.log('error')
		})*/

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



	$.ajax({
				    type: 'POST',
				    url: 'http://localhost:8080/#/signup',
				    data: JSON.stringify({'fullname': name , 'email': email, 'password':password}),
				    contentType: 'application/json',
				    success: function(data,textStatus, jqXHR) {
				        console.log('POST response: ');
				        console.log(data);
					    }
					});


};



});