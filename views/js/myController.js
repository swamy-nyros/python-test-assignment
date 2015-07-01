var app = angular.module('MyWebApp', ['ngRoute']);

app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.        
        when('/', {
            templateUrl: 'views/main.html',
            controller: 'myController'

        }).
        when('/signup', {
            templateUrl: 'views/signup.html',
            controller: 'myController'
                              
        }).
        when('/login', {
            templateUrl: 'views/login.html',
                              
        }).
        otherwise({
            redirectTo: '/'
        });
}]);

app.controller("myController", function($scope) {

	$scope.name="swamy";

/*	$scope.SignUp = function() {
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


});