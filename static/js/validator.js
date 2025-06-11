// Bản thân func cũng là một obj
// Đối tượng `Validator`
function Validator(options) {
    
    function getParent(element, selector) {
        while (element.parentElement) {
            if (element.parentElement.matches(selector)) { // matches trong DOM giúp kiểm tra xem có css selector nào match hay k
                return element.parentElement;
            }
                element = element.parentElement; 
        }
    }
    var selectorRules = {};

    // Hàm thực hiện validate
    function validate(inputElement, rule) {
        var errorElement = getParent(inputElement, options.formGroupSelector).querySelector(options.errorSelector);
        var errorMessages;

        // Lấy ra các rules của selector
        var rules = selectorRules[rule.selector];

        // Lặp qua từng rule và kiểm tra
        // Nếu có lỗi thì dừng việc kiểm tra
        for (var i = 0; i < rules.length; i++) {
            switch (inputElement.type) {
                case 'radio':
                case 'checkbox':
                    errorMessages = rules[i](
                        formElement.querySelector(rule.selector + ':checked')
                    );
                    break;
                default: 
                    errorMessages = rules[i](inputElement.value);
            }
            if (errorMessages) break;
        }

                if (errorMessages) {
                    errorElement.innerText = errorMessages;
                    getParent(inputElement, options.formGroupSelector).classList.add('invalid');
                    getParent(inputElement, options.formGroupSelector).classList.remove('valid');
                }
                else {
                    errorElement.innerText = '';
                    getParent(inputElement, options.formGroupSelector).classList.remove('invalid');
                    getParent(inputElement, options.formGroupSelector).classList.add('valid');
                }
        return !!errorMessages
    }

    // Lấy element của form cần validate
    var formElement = document.querySelector(options.form)

    if (formElement) {
        // Khi submit form
        formElement.onsubmit = function(e) {
            e.preventDefault();

            var isFormValid = true;
            // Thực hiện lặp qua từng rule
            options.rules.forEach(function (rule) {
                var inputElement = formElement.querySelector(rule.selector)
                
                var isValid = validate(inputElement, rule)
                if (isValid) {
                    isFormValid = false;
                }
            });

            

            if (isFormValid)  {
                // Trường hợp submit với javascript
                // if (typeof options.onSubmit === 'function') {
                    
                //     var enableInputs = formElement.querySelectorAll('[name]:not([disabled])'); // [] dùng để chọn attr
                    
                //     var formValues = Array.from(enableInputs).reduce(function (values, input) {
                //         switch (input.type) {
                //             case  'radio':
                //                 values[input.name] = formElement.querySelector('[name="' + input.name + '"]:checked').value;
                //                 break;
                //             case 'checkbox':
                //                 if (!input.matches(':checked')) return values;
                //                 if (!Array.isArray(values[input.name])) {
                //                     values[input.name] = [];
                //                 }
                //                 values[input.name].push(input.value);

                //                 break;
                //             default: 
                //                 values[input.name] = input.value;
                //         }
                //         return values; // trả về thg values là thằng cuối cùng 
                //     }, {}); // là một obj tích lũy sau khi thêm một key:value
                    
                //     options.onSubmit(formValues);
                // }
                // Trường hợp submit với hành vi mặc định của trình duyệt
                formElement.submit();

            }   
        }

        // Lặp qua mỗi rule và xử lý (lắng nghe sự kiện blur, input, ...)
        options.rules.forEach(function (rule) {

            // Lưu lại các rules cho mỗi input  
            if (Array.isArray(selectorRules[rule.selector])) {
                selectorRules[rule.selector].push(rule.test);
            }
            else {
                selectorRules[rule.selector] = [rule.test];
            }
            

            var inputElements = formElement.querySelectorAll(rule.selector)

            Array.from(inputElements).forEach(function(inputElement) {
                // Xử lý trường hợp blur ra khỏi input
                inputElement.onblur = function () {
                    validate(inputElement, rule);
                }
    
                // Xử lý khi người dùng nhập vào input
                inputElement.oninput = function () {
                    var errorElement = getParent(inputElement, options.formGroupSelector).querySelector(options.errorSelector)
                    errorElement.innerText = '';
                    getParent(inputElement, options.formGroupSelector).classList.remove('invalid');
                }   
            });  
    
        })
    }     
}

// Định nghĩa rules
// Nguyên tắc của các rules:
// 1. Khi có lỗi thì trả ra message lỗi 
// 2. Khi hợp lệ thì không trả ra cái gì cả (undefined)
Validator.isRequired = function (selector, message) {
    return {
        selector: selector,
        test: function (value) {
            return value ? undefined : message || 'Vui lòng nhập trường này'
        }
    };
}

Validator.isEmail = function (selector, message) {
   return {
        selector: selector,
        test: function (value) {
            var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
            return regex.test(value) ? undefined : message || 'Trường này phải là email';
        }
    };
}

Validator.minLength = function (selector, min, message) {
    return {
         selector: selector,
         test: function (value) {
             return value.length >= min ? undefined : message || `Password required a minimum of ${min} characters`;
         }
     };
}

Validator.isConfirmed = function (selector, getConfirmValue, message) {
    return {
        selector: selector,
        test: function(value) {
            return value === getConfirmValue() ? undefined : message || 'Giá trị nhập vào không chính xác'
        }
    }
}
