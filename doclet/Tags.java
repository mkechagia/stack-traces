/*
 * Copyright 2014 Maria Kechagia
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.*;
import com.sun.javadoc.*;

/*
 * This class reads a java file and returns specific tags.
 *
 */
public class Tags {
    public static boolean start(RootDoc root) { 
        String tagName = "@hide";
        writeContents(root.classes(), tagName);
        return true;
    }

    public static void writeContents(ClassDoc[] classes, String tagName) {
        boolean classNamePrinted = false;
        int c = 0; // counts the number of parsed classes
        int m = 0; // counts the number of parsed methods
        int t = 0; // counts the found @throws comments
        int e = 0; // counts the found method exceptions 
        int h = 0; // counts the found @hide comments

        for (int i=0; i < classes.length; i++) {
            classNamePrinted = true;
            c = c + 1;

            // array of methods founds
            MethodDoc[] methods = classes[i].methods();
            for (int j=0; j < methods.length; j++) {
                // print method details
                System.out.println("Method:" + methods[j].name() + methods[j].flatSignature());
                m = m + 1; 

                // for @hide method comments
                Tag[] hids = methods[j].tags(tagName);
                // for @throws method comments
                ThrowsTag[] tags = methods[j].throwsTags();
                // for throw next to the method signature
                Type[] exceptions = methods[j].thrownExceptionTypes();

                if (hids.length > 0) {
                    for (int k = 0; k < hids.length; k++) {
                        System.out.println("Hidden:" + hids[k].name());
                        h = h + 1;
                    }
                }
                if (tags.length > 0) {
                    for (int k=0; k < tags.length; k++) {
                        System.out.println("Throws:" + tags[k].exceptionName());
                        t = t + 1;
                    }
                } 
                if (exceptions.length > 0) {
                    for (int l=0; l < exceptions.length; l++) {
                        System.out.println("Exception:" + exceptions[l]);
                        e = e + 1;
                    }
                }
            } 
        }

        System.out.println("\nNo of classes: " + c);
        System.out.println("No of methods: " + m);
        System.out.println("No of @throws: " + t);
        System.out.println("No of signature exceptions: " + e);
        System.out.println("No of @hide: " + h);
    }
}