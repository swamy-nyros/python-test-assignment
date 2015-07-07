var app = angular.module('myApp', ['ngRoute']);

app.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider. 
     when('/', {
            templateUrl: 'static/templates/home.html'            

        }).       
        when('/signup', {
            templateUrl: 'static/templates/signup.html'            
                              
        }).
        when('/login', {
            templateUrl: 'static/templates/login.html'
                              
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

app.controller("MainController", function($scope, $rootScope, $http, $log, $location,$route, $window) {

$scope.fields = {};
$scope.alerts = '';
$scope.users = '';
$scope.messages = '';
$scope.stat = '';


	$scope.submitMyForm=function(){
        $http({
             method: 'POST',
             url: '/signup',
             data: { fullname: $scope.fields.name , email: $scope.fields.email , $route, password: $scope.fields.password }
             }).
             success(function (data, status, headers, config) {
             	// $rootScope.guests = data;
             	console.log("success, need to show message and redirect to login");
             	// console.log(data[0].status_message);
             	console.log(data.status_message);
             	console.log(status);
             	$scope.alerts = data;
      			if (data.status_message=="Error"){
             		$location.path('/signup');
             	} else {
             		$location.path('/login');
             	}
             }).
             error(function (data, status, headers, config) {
             	console.log("Error, may be duplicate email");
             	console.log(data);
             	console.log(status);
      			$rootScope.status = 'Error';
      			$location.path('/signup');
             });
        
    }

    $scope.submitMyForm1=function(){
        console.log("entering to messages")
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
                if (data.status_message=="Error"){
                    $location.path('/usermessage');
                } else {
                    $location.path('/message');
                }
                
             }).
             error(function (data, status, headers, config) {
                console.log("Error, may be duplicate email");
                console.log(data);
                console.log(status);
                // $rootScope.guests.push(data);
                $rootScope.status = 'Error';
                $location.path('/usermessage');
             });
    }

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
             }).
             error(function (data, status, headers, config) {
                console.log("error")
                console.log(data)
             });
$scope.current_user = '';
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
                console.log(data.curren_user)
                console.log(data.stat)

             	$scope.users = data.userlist;
                $scope.current_user = data.curren_user;
                $scope.messages = data.messagelist;
                $scope.stat = data.stat;
                if (data.stat=="invalid user"){
                    $location.path('/login');
                } else {
                    $location.path('/message');
                }
             	
                
             }).
             error(function (data, status, headers, config) {
                console.log("OK")
             	console.log(data)
             });

    }
    $scope.logout=function(){
       
    $http({
        method: "GET",
        url: '/logout',
        data: { fullname: $scope.fields.name , password: $scope.fields.password }
        }).
        success(function (data, status, headers, config) {
            
            console.log(data)
            $scope.user = [];
            $("#info").html('');
            $location.path('/login');
        }).
        error(function (data, status, headers, config) {
            console.log("error")
            console.log(data)
        })

    }
   

});

