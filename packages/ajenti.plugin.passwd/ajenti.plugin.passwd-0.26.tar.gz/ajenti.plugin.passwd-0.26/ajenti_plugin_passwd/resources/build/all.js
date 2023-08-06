'use strict';

angular.module('ajenti.passwd', ['core']);


'use strict';

angular.module('ajenti.passwd').service('passwd', function ($http, $q) {
    this.list = function () {
        return $http.get("/api/passwds").then(function (response) {
            return response.data;
        });
    };

    this.set = function (user, password) {
        return $http.post("/api/passwd", { user: user, password: password }).then(function (response) {
            return response.data;
        });
    };

    return this;
});


