'''
    element base operation
'''

import sys
from typing import Union
from clicknium.common.enums import *
from clicknium.common.constants import _Constants
from clicknium.common.models.clicklocation import ClickLocation
from clicknium.common.models.elementitem import ElementPosition, ElementSize
from clicknium.common.models.exceptions import ArgumentError
from clicknium.common.utils import Utils
from clicknium.core.service.invokerservice import _ConvertBaseTypeService, _ConvertOptionService, _ExceptionHandle

if sys.version_info >= (3, 8):
    from typing import Literal
else: 
    from typing_extensions import Literal

class UiElement(object):

    def __init__(self, element):
        self._element = element

    @property
    @_ExceptionHandle.try_except
    def parent(self):
        """
            Get parent element.
                                
            Returns:
                UiElement object if it was found, or None if not
        """
        if self._element.Parent:
            return UiElement(self._element.Parent)
        return None

    @property
    @_ExceptionHandle.try_except
    def children(self):
        """
            Get element's children elements.
                                
            Returns:
                list of UiElement object, a list with elements if any was found or an empty list if not
        """
        child_list = []
        if self._element.Children:            
            for child in self._element.Children:
                child_list.append(UiElement(child))
        return child_list

    @property
    @_ExceptionHandle.try_except
    def next_sibling(self):
        """
            Get next sibling element.
                                
            Returns:
                UiElement object if it was found, or None if not
        """
        if self._element.NextSibling:
            return UiElement(self._element.NextSibling)
        return None

    @property
    @_ExceptionHandle.try_except
    def previous_sibling(self):
        """
            Get previous sibling element.
                                
            Returns:
                UiElement object if it was found, or None if not
        """
        if self._element.PreviousSibling:
            return UiElement(self._element.PreviousSibling)
        return None
    
    @_ExceptionHandle.try_except
    def child(self, index: int):
        """
            Get child element with its index.

            Parameters:
                index: index specified, get the nth child
                                
            Returns:
                UiElement object if it was found, or None if not
        """
        child_element = self._element.Child(index)
        if child_element:
            return UiElement(self._element.Child(index))
        return None

    @_ExceptionHandle.try_except
    def click(
        self,
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        click_location: ClickLocation = ClickLocation(),
        click_method: Union[Literal["default", "mouse-emulation", "control-invocation"], ClickMethod] = ClickMethod.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        timeout: int = 30
    ) -> None:        
        """
            Click an element with single click.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                mouse_button: mouse button is set to define the mouse button to click. Default value is left, it will click with mouse left button

                click_location: click location is set to define the element position to click. Default value is center, it will click the element's center position
 
                click_method: click method is set to which method to use when clicking the element. Default vaule is default  
                    mouse-emulation: perform mouse emulator, will move mouse to the target element and click
                    control-invocation: invoke the action on the target element, for web element, perform through javascript; for windows application element, it should support the action, or will be failed
                    default: for web element, will use control-invocation; for window element, will use mouse-emulation

                modifier_key: modifier key is set to click with the modifier key("alt", "ctrl", "shift","win"). Default vaule is none

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                            
            Returns:
                None
        """
        click_option = _ConvertOptionService.convert_clickoption(ClickType.Click, mouse_button, click_location.Location, click_method, modifier_key, click_location.Xoffset, click_location.Yoffset, click_location.Xrate, click_location.Yrate)
        self._element.Click(click_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def double_click(
        self,
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        click_location: ClickLocation = ClickLocation(),
        click_method: Union[Literal["default", "mouse-emulation", "control-invocation"], ClickMethod] = ClickMethod.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        timeout: int = 30
    ) -> None:        
        """
            Click an element with double click.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                mouse_button: mouse button is set to define the mouse button to click. Default value is left, it will click with mouse left button

                click_location: click location is set to define the element position to click. Default value is center, it will click the element's center position
 
                click_method: click method is set to which method to use when clicking the element. Default vaule is default  
                    mouse-emulation: perform mouse emulator, will move mouse to the target element and click
                    control-invocation: invoke the action on the target element, for web element, perform through javascript; for windows application element, it should support the action, or will be failed
                    default: for web element, will use control-invocation; for window element, will use mouse-emulation

                modifier_key: modifier key is set to click with the modifier key("alt", "ctrl", "shift","win"). Default vaule is none

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None

        """
        click_option = _ConvertOptionService.convert_clickoption(ClickType.DoubleClick, mouse_button, click_location.Location, click_method, modifier_key, click_location.Xoffset, click_location.Yoffset, click_location.Xrate, click_location.Yrate)
        self._element.Click(click_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def mouse_up(
        self,
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        click_location: ClickLocation = ClickLocation(),
        click_method: Union[Literal["default", "mouse-emulation", "control-invocation"], ClickMethod] = ClickMethod.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        timeout: int = 30
    ) -> None:        
        """
            Mouse key up on an element.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                mouse_button: mouse button is set to define the mouse button to click. Default value is left, it will click with mouse left button

                click_location: click location is set to define the element position to click. Default value is center, it will click the element's center position
 
                click_method: click method is set to which method to use when clicking the element. Default vaule is default  
                    mouse-emulation: perform mouse emulator, will move mouse to the target element and click
                    control-invocation: invoke the action on the target element, for web element, perform through javascript; for windows application element, it should support the action, or will be failed
                    default: for web element, will use control-invocation; for window element, will use mouse-emulation

                modifier_key: modifier key is set to click with the modifier key("alt", "ctrl", "shift","win"). Default vaule is none

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None

        """
        click_option = _ConvertOptionService.convert_clickoption(ClickType.Up, mouse_button, click_location.Location, click_method, modifier_key, click_location.Xoffset, click_location.Yoffset, click_location.Xrate, click_location.Yrate)
        self._element.Click(click_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def mouse_down(
        self,
        mouse_button: Literal["left", "middle", "right"] = MouseButton.Left,
        click_location: ClickLocation = ClickLocation(),
        click_method: Union[Literal["default", "mouse-emulation", "control-invocation"], ClickMethod] = ClickMethod.Default,
        modifier_key: Literal["nonekey", "alt", "ctrl", "shift","win"]  = ModifierKey.NoneKey,
        timeout: int = 30
    ) -> None:        
        """
            Mouse key down on an element.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                mouse_button: mouse button is set to define the mouse button to click. Default value is left, it will click with mouse left button

                click_location: click location is set to define the element position to click. Default value is center, it will click the element's center position
 
                click_method: click method is set to which method to use when clicking the element. Default vaule is default  
                    mouse-emulation: perform mouse emulator, will move mouse to the target element and click
                    control-invocation: invoke the action on the target element, for web element, perform through javascript; for windows application element, it should support the action, or will be failed
                    default: for web element, will use control-invocation; for window element, will use mouse-emulation

                modifier_key: modifier key is set to click with the modifier key("alt", "ctrl", "shift","win"). Default vaule is none

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None

        """
        click_option = _ConvertOptionService.convert_clickoption(ClickType.Down, mouse_button, click_location.Location, click_method, modifier_key, click_location.Xoffset, click_location.Yoffset, click_location.Xrate, click_location.Yrate)
        self._element.Click(click_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def send_hotkey(
        self,
        hotkey: str,
        preaction: Literal["setfocus", "click"] = PreAction.SetFocus,
        timeout: int = 30
    ) -> None: 
        """
            Send hot key based on target element.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                hotkey[Required]: hotkey string, can be one key or combined keys, each key is represented by one or more characters. To specify a single keyboard character, use the character itself. For example, to represent the letter A, pass in the string "A" to the method. To represent more than one character, append each additional character to the one preceding it. To represent the letters A, B, and C, specify the parameter as "ABC". For special keys, please refer to https://docs.microsoft.com/en-au/dotnet/api/system.windows.forms.sendkeys?view=windowsdesktop-6.0#remarks

                preaction: before send hotkey, which action should be taken on the target element

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        sendhotkey_option = _ConvertOptionService.convert_sendhotkey_option(preaction)       
        self._element.SendHotKey(hotkey, sendhotkey_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def drag_drop(
        self,
        xpoint: int = 0,
        ypoint: int = 0,
        speed: int = 50,
        timeout: int = 30
    ) -> None:
        """
            Holds down the left mouse button on the source element, then moves to the target offset and releases the mouse button.
 
            Parameters:

                xpoint: pixels of X-Axis will be moved

                ypoint: pixels of X-Axis will be moved

                speed: drag speed. The unit of parameter is ms/10px. Default is 50

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        dragdrop_option = _ConvertOptionService.convert_dragdrop_option(xpoint, ypoint, speed)
        self._element.DragDrop(dragdrop_option, timeout*1000)

    @_ExceptionHandle.try_except
    def hover(self, timeout: int = 30) -> None:
        """
            Hover on the element, the mouse will move upon the element for a while.
 
            Parameters:

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        self._element.Hover(timeout * 1000)

    @_ExceptionHandle.try_except
    def set_checkbox(
        self,
        check_type: Literal["check", "uncheck", "toggle"] = CheckType.Check,
        timeout: int = 30
    ) -> None:
        """
            Do check operation on target element.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                check_type: set option for check operation, "check", "uncheck" or "toggle"

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        check_option = _ConvertOptionService.convert_check_option(check_type)
        self._element.Check(check_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def set_text(
        self,
        text: str,
        input_method: Union[Literal["default", "set-text", "sendkey-after-click", "sendkey-after-focus"], InputMethod]= InputMethod.SetText,
        timeout: int = 30
    ) -> None:
        """
            Set text for the target element.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                text[Requried]: text string, is set to be input

                input_method: the input method for the set text opeartion  
                    set-text: invoke the action on the target element, for web element, perform through javascript; for windows application element, it should support the action, or will be failed
                    sendkey-after-click: click(mouse emulator) the target element first and then input text through keyboard simulate
                    sendkey-after-focus: set focus on the target element first and then input text through keyboard simulate
                    default: for web element, will use controlinvocation; for window element, will use sendkey-after-click

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        settext_option = _ConvertOptionService.convert_settext_option(input_method)
        self._element.SetText(text,settext_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def clear_text(
        self,
        clear_method: Union[Literal["set-text", "send-hotkey"], ClearMethod],
        clear_hotkey: Union[Literal["CAD", "ESHD", "HSED"], ClearHotKey] = ClearHotKey.CtrlA_Delete,
        preaction: Literal["setfocus", "click"] = PreAction.SetFocus,
        timeout: int = 30
    ) -> None:
        """
            Clear the element's text.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                clear_method: clear method, the method to clear text for the target element  
                    set-text: invoke the action on the target element, for web element, perform through javascript; for window element, it should support the action, or will be failed
                    send-hotkey: through send hotkey to clear text on the target element, need specify "clear_hotkey" parameter

                clear_hotkey: clear hotkey, default is {CTRL}{A}{DELETE}  
                    CAD: {CTRL}{A}-{DELETE}, send the combined hotkey "{CTRL}{A}" first, then send hotkey "{DELETE}"
                    ESHD: {END}{SHIFT}{HOME}{DELETE}, send the hotkey "{END}" first, then send combined hotkey "{SHIFT}{HOME}, then send hotkey "{DELETE}"
                    HSED: {HOME}{SHIFT}{END}{DELETE}, send the hotkey "{HOME}" first, then send combined hotkey "{SHIFT}{END}, then send hotkey "{DELETE}"

                preaction: pre action, before clear text, which action should be taken on the target element

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        cleartext_option = _ConvertOptionService.convert_cleartext_option(clear_method, clear_hotkey, preaction)
        self._element.ClearText(cleartext_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def get_text(self, timeout: int = 30) -> str:
        """
            Get text of the element.
 
            Parameters:

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds

            Returns:
                str
        """
        return self._element.GetText(timeout * 1000)

    @_ExceptionHandle.try_except
    def get_property(
        self,
        name: str,
        timeout: int = 30
    ) -> str:
        """
            Get the given property of the element.
 
            Parameters:

                name[Required]: property name, different ui elements may support different property list, for general property list, please refer to https://clicknium.github.io/product-docs/#/./doc/automation/property

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds

            Returns:
                str
        """
        return self._element.GetProperty(name, timeout * 1000)

    @_ExceptionHandle.try_except
    def select_item(
        self,
        item: str,
        timeout: int = 30
    ) -> None:
        """
            Select one option for the target.
 
            Parameters:

                item[Required]: option of the dropdown control, the control support selection, such as select element in web, or combobox in window apllcaiton

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        self._element.SelectItem(item, timeout * 1000)

    @_ExceptionHandle.try_except
    def select_items(
        self,
        items: list,
        clear_selected: bool = True,
        timeout: int = 30
    ) -> None:
        """
            Select multiple option for the target.
 
            Parameters:

                items[Required]: options of the dropdown control, the control should support multiple selection

                clear_selected: whether need deselect the already selected options of target control, default is True

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        items_array = _ConvertBaseTypeService.convert_array(items)
        select_items_option = _ConvertOptionService.convert_select_items_option(clear_selected)
        self._element.SelectMultipleItem(items_array, select_items_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def save_to_image(
        self,
        image_file: str,
        img_width: int = 0,
        img_height: int = 0,
        xoffset: int = 0,
        yoffset: int  = 0,
        timeout: int = 30
    ) -> None:
        """
            Save target element's screenshot to file with specified size and offset.
 
            Parameters:

                image_file[Required]: file path to save image

                img_width: image width. Default 0, will use target element's screenshot real width

                img_height: image height. Default 0, will use target element's screenshot real height

                xoffset: offset of X-Axis, Default 0, means not offset

                yoffset: offset of Y-Axis, Default 0, means not offset

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """        
        save_image_option = _ConvertOptionService.convert_save_image_option(img_width, img_height, xoffset, yoffset)
        image = self._element.CaptureScreenShot(save_image_option, timeout * 1000)
        Utils.create_file(image_file)
        image.Save(image_file)

    @_ExceptionHandle.try_except
    def highlight(
        self,
        color: Union[str, Color] = Color.Yellow,
        duration: int = 3,        
        timeout: int = 30
    ) -> None: 
        """
            Highlight the element with specified color.

            Remarks: Import parameter's module with " from clicknium.common.enums import * "
 
            Parameters:

                color: the color of the highlighting rectangle, default is Yellow

                duration: the duration for highlighting the element. The unit of parameter is second. Default is set to 3 seconds                

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                                
            Returns:
                None
        """
        if len(color) != 7:
            raise ArgumentError(_Constants.InvalidColor)
        color = color.lower().replace("#","#ff")
        highlight_option = _ConvertOptionService.convert_highlight_option(duration, color)  
        self._element.Highlight(highlight_option, timeout * 1000)

    @_ExceptionHandle.try_except
    def set_focus(self, timeout: int = 30) -> None:
        """
            Set focus for the target element.
 
            Parameters:

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds
                
            Returns:
                None
        """
        self._element.SetFocus(timeout * 1000)

    @_ExceptionHandle.try_except
    def get_position(self, timeout: int = 30) -> ElementPosition:
        """
            Get element's position.
 
            Parameters:

                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds

            Returns:
                ElementPosition
        """
        rectangle = self._element.GetLocation(timeout * 1000)
        return ElementPosition(rectangle.Left, rectangle.Top, rectangle.Right, rectangle.Bottom) if rectangle else None

    @_ExceptionHandle.try_except
    def get_size(self, timeout: int = 30) -> ElementSize:
        """
            Get element's size(height and width).
 
            Parameters:
                timeout: timeout for the operation. The unit of parameter is seconds. Default is set to 30 seconds

            Returns:
                ElementSize
        """
        rectangle = self._element.GetLocation(timeout * 1000)
        return ElementSize(rectangle.Width, rectangle.Height) if rectangle else None

    @_ExceptionHandle.try_except
    def wait_property(
        self,
        name: str, 
        value: str, 
        wait_timeout: int = 30
    ) -> bool:
        """
            Wait element's property appears in given time.
 
            Parameters:
                name[Required]: property name, different ui elements may support different property list, for general property list, please refer to https://clicknium.github.io/product-docs/#/./doc/automation/property

                value[Required]: expected property value

                wait_timeout: wait timeout for the operation, unit is second, default value is 30 seconds
 
            Returns:
                bool, return True if ui element exist and the property value equals expected value, or return False
        """        
        result = self._element.WaitProperty(name, value, wait_timeout * 1000)
        return True if result else False