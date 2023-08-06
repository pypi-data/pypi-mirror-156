#-------------------------------------------------------------------------------------------------------------------------------

#          pienex 1.0 (propositional logic)

#             © 2022 Alejandro Ascárate

#-------------------------------------------------------------------------------------------------------------------------------


#total_number_of_3tpls gives the total number of nested 3-tuples.

def total_number_of_3tpls(nested_tpls):
	count = 1
	lst = list (list (nested_tpls))
	i=1
	while type (())==type (lst[0]) or type (())==type (lst[2]):
		if type (())==type (lst[2]):
			lst = list (list (lst).pop(2))
			count+=1
		if type (())==type (lst[0]):
			lst = list (list (lst).pop(0))
			count+=1
		i+=1
	return count


#nth_innermost_3tpl gives the 3-tuple that results afer the (total+1-n) iteration of the binary 
#logical operations on the initial one.

def nth_innermost_3tpl(nested_tpls, n):
	if n==1:
		return nested_tpls
	else:
		count = 1
		lst = list (list (nested_tpls))
		i=1
		while type (())==type (lst[0]) or type (())==type (lst[2]):
			if type (())==type (lst[2]):
				lst = list (list (lst).pop(2))
				count+=1
				if count==n:
					break
			if type (())==type (lst[0]):
				lst = list (list (lst).pop(0))
				count+=1
				if count==n:
					break
			i+=1
		return tuple (lst)	


#lst_of_all_3tpls gives the list of all 3-tuples, in ascending order from innermost to outermost.

def lst_of_all_3tpls(nested_tpls):
	lst = []
	for n in range (total_number_of_3tpls(nested_tpls), 0, -1):
		lst.append(nth_innermost_3tpl(nested_tpls, n))
	return lst


import numpy as np 
import keras 
from keras.models import load_model
from tensorflow.keras import layers
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical


#nth_stage_neg_0(nested_tpls, n) builds and trains the network corresponding to the negative at the left in the nth 3-tuple from the list.

def nth_stage_neg_0(nested_tpls, n):
	if type (lst_of_all_3tpls(nested_tpls)[n-1][0])!=type (()) and lst_of_all_3tpls(nested_tpls)[n-1][0] < 0:
		N_ = lst_of_all_3tpls(nested_tpls)[n-1][0]
		N = abs (lst_of_all_3tpls(nested_tpls)[n-1][0])
		X_train, y_train = np.loadtxt(f"X_train_{N}.csv", delimiter=","), np.loadtxt(f"y_train_{N}.csv", delimiter=",")
		X_test, y_test = np.loadtxt(f"X_test_{N}.csv", delimiter=","), np.loadtxt(f"y_test_{N}.csv", delimiter=",")
		pretrained_model = load_model(f"{N}.h5")
		intermediate_layer_model = keras.Model(inputs=pretrained_model.input, outputs=pretrained_model.get_layer("dense_1").output)
		X_train_intermediate_output = intermediate_layer_model(X_train)
		X_test_intermediate_output = intermediate_layer_model(X_test)
		np.savetxt(f"X_train_{N_}.csv", X_train_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N_}.csv", X_test_intermediate_output, delimiter=",")
		y_train_neg = [0 if y_train[i]==1 else 1 for i in range (0, y_train.shape[0])]
		y_test_neg = [0 if y_test[i]==1 else 1 for i in range (0, y_test.shape[0])]
		np.savetxt(f"y_train_{N_}.csv", y_train_neg, delimiter=",")
		np.savetxt(f"y_test_{N_}.csv", y_test_neg, delimiter=",")
		num = X_train_intermediate_output.shape[1]
		y_train_neg = to_categorical(y_train_neg)
		y_test_neg = to_categorical(y_test_neg)
		num_classes = y_test_neg.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.layers[0]._name = "dense_1"
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_intermediate_output, y_train_neg, validation_data=(X_test_intermediate_output, y_test_neg), epochs=100, verbose=2)
		scores = model.evaluate(X_test_intermediate_output, y_test_neg, verbose=0)
		print (str (N_) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N_}.h5")


#nth_stage_neg_2(nested_tpls, n) builds and trains the network corresponding to the negative at the right in the nth 3-tuple from the list.

def nth_stage_neg_2(nested_tpls, n):
	if type (lst_of_all_3tpls(nested_tpls)[n-1][2])!=type (()) and lst_of_all_3tpls(nested_tpls)[n-1][2] < 0:
		N_ = lst_of_all_3tpls(nested_tpls)[n-1][2]
		N = abs (lst_of_all_3tpls(nested_tpls)[n-1][2])
		X_train, y_train = np.loadtxt(f"X_train_{N}.csv", delimiter=","), np.loadtxt(f"y_train_{N}.csv", delimiter=",")
		X_test, y_test = np.loadtxt(f"X_test_{N}.csv", delimiter=","), np.loadtxt(f"y_test_{N}.csv", delimiter=",")
		pretrained_model = load_model(f"{N}.h5")
		intermediate_layer_model = keras.Model(inputs=pretrained_model.input, outputs=pretrained_model.get_layer("dense_1").output)
		X_train_intermediate_output = intermediate_layer_model(X_train)
		X_test_intermediate_output = intermediate_layer_model(X_test)
		np.savetxt(f"X_train_{N_}.csv", X_train_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N_}.csv", X_test_intermediate_output, delimiter=",")
		y_train_neg = [0 if y_train[i]==1 else 1 for i in range (0, y_train.shape[0])]
		y_test_neg = [0 if y_test[i]==1 else 1 for i in range (0, y_test.shape[0])]
		np.savetxt(f"y_train_{N_}.csv", y_train_neg, delimiter=",")
		np.savetxt(f"y_test_{N_}.csv", y_test_neg, delimiter=",")
		num = X_train_intermediate_output.shape[1]
		y_train_neg = to_categorical(y_train_neg)
		y_test_neg = to_categorical(y_test_neg)
		num_classes = y_test_neg.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.layers[0]._name = "dense_1"
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_intermediate_output, y_train_neg, validation_data=(X_test_intermediate_output, y_test_neg), epochs=100, verbose=2)
		scores = model.evaluate(X_test_intermediate_output, y_test_neg, verbose=0)
		print (str (N_) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N_}.h5")


#nth_stage(nested_tpls, n) builds and trains the network corresponding to the nth 3-tuple from the list.

def nth_stage(nested_tpls, n):
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==1:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		X_train_a, y_train_a = np.loadtxt(f"X_train_{N_a}.csv", delimiter=","), np.loadtxt(f"y_train_{N_a}.csv", delimiter=",")
		X_test_a, y_test_a = np.loadtxt(f"X_test_{N_a}.csv", delimiter=","), np.loadtxt(f"y_test_{N_a}.csv", delimiter=",")
		X_train_c, y_train_c = np.loadtxt(f"X_train_{N_c}.csv", delimiter=","), np.loadtxt(f"y_train_{N_c}.csv", delimiter=",")
		X_test_c, y_test_c = np.loadtxt(f"X_test_{N_c}.csv", delimiter=","), np.loadtxt(f"y_test_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		X_train_a_intermediate_output = intermediate_layer_model_a(X_train_a)
		X_test_a_intermediate_output = intermediate_layer_model_a(X_test_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		X_train_c_intermediate_output = intermediate_layer_model_c(X_train_c)
		X_test_c_intermediate_output = intermediate_layer_model_c(X_test_c)
		X_train_concat_intermediate_output = np.concatenate ((X_train_a_intermediate_output, X_train_c_intermediate_output), axis=1)
		X_test_concat_intermediate_output = np.concatenate ((X_test_a_intermediate_output, X_test_c_intermediate_output), axis=1)
		np.savetxt(f"X_train_{N}.csv", X_train_concat_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N}.csv", X_test_concat_intermediate_output, delimiter=",")
		y_train_b = [1 if (y_train_a[i]==1 and y_train_c[i]==1) else 0 for i in range (0, y_train_a.shape[0])]
		y_test_b = [1 if (y_test_a[i]==1 and y_test_c[i]==1) else 0 for i in range (0, y_test_a.shape[0])]
		np.savetxt(f"y_train_{N}.csv", y_train_b, delimiter=",")
		np.savetxt(f"y_test_{N}.csv", y_test_b, delimiter=",")
		num = X_train_concat_intermediate_output.shape[1]
		y_train_b = to_categorical(y_train_b)
		y_test_b = to_categorical(y_test_b)
		num_classes = y_test_b.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_concat_intermediate_output, y_train_b, validation_data=(X_test_concat_intermediate_output, y_test_b), epochs=100, verbose=2)
		scores = model.evaluate(X_test_concat_intermediate_output, y_test_b, verbose=0)
		print (str (N) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N}.h5")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==2:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		X_train_a, y_train_a = np.loadtxt(f"X_train_{N_a}.csv", delimiter=","), np.loadtxt(f"y_train_{N_a}.csv", delimiter=",")
		X_test_a, y_test_a = np.loadtxt(f"X_test_{N_a}.csv", delimiter=","), np.loadtxt(f"y_test_{N_a}.csv", delimiter=",")
		X_train_c, y_train_c = np.loadtxt(f"X_train_{N_c}.csv", delimiter=","), np.loadtxt(f"y_train_{N_c}.csv", delimiter=",")
		X_test_c, y_test_c = np.loadtxt(f"X_test_{N_c}.csv", delimiter=","), np.loadtxt(f"y_test_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		X_train_a_intermediate_output = intermediate_layer_model_a(X_train_a)
		X_test_a_intermediate_output = intermediate_layer_model_a(X_test_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		X_train_c_intermediate_output = intermediate_layer_model_c(X_train_c)
		X_test_c_intermediate_output = intermediate_layer_model_c(X_test_c)
		X_train_concat_intermediate_output = np.concatenate ((X_train_a_intermediate_output, X_train_c_intermediate_output), axis=1)
		X_test_concat_intermediate_output = np.concatenate ((X_test_a_intermediate_output, X_test_c_intermediate_output), axis=1)
		np.savetxt(f"X_train_{N}.csv", X_train_concat_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N}.csv", X_test_concat_intermediate_output, delimiter=",")
		y_train_b = [0 if (y_train_a[i]==0 and y_train_c[i]==0) else 1 for i in range (0, y_train_a.shape[0])]
		y_test_b = [0 if (y_test_a[i]==0 and y_test_c[i]==0) else 1 for i in range (0, y_test_a.shape[0])]
		np.savetxt(f"y_train_{N}.csv", y_train_b, delimiter=",")
		np.savetxt(f"y_test_{N}.csv", y_test_b, delimiter=",")
		num = X_train_concat_intermediate_output.shape[1]
		y_train_b = to_categorical(y_train_b)
		y_test_b = to_categorical(y_test_b)
		num_classes = y_test_b.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_concat_intermediate_output, y_train_b, validation_data=(X_test_concat_intermediate_output, y_test_b), epochs=100, verbose=2)
		scores = model.evaluate(X_test_concat_intermediate_output, y_test_b, verbose=0)
		print (str (N) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N}.h5")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==3:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		X_train_a, y_train_a = np.loadtxt(f"X_train_{N_a}.csv", delimiter=","), np.loadtxt(f"y_train_{N_a}.csv", delimiter=",")
		X_test_a, y_test_a = np.loadtxt(f"X_test_{N_a}.csv", delimiter=","), np.loadtxt(f"y_test_{N_a}.csv", delimiter=",")
		X_train_c, y_train_c = np.loadtxt(f"X_train_{N_c}.csv", delimiter=","), np.loadtxt(f"y_train_{N_c}.csv", delimiter=",")
		X_test_c, y_test_c = np.loadtxt(f"X_test_{N_c}.csv", delimiter=","), np.loadtxt(f"y_test_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		X_train_a_intermediate_output = intermediate_layer_model_a(X_train_a)
		X_test_a_intermediate_output = intermediate_layer_model_a(X_test_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		X_train_c_intermediate_output = intermediate_layer_model_c(X_train_c)
		X_test_c_intermediate_output = intermediate_layer_model_c(X_test_c)
		X_train_concat_intermediate_output = np.concatenate ((X_train_a_intermediate_output, X_train_c_intermediate_output), axis=1)
		X_test_concat_intermediate_output = np.concatenate ((X_test_a_intermediate_output, X_test_c_intermediate_output), axis=1)
		np.savetxt(f"X_train_{N}.csv", X_train_concat_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N}.csv", X_test_concat_intermediate_output, delimiter=",")
		y_train_b = [0 if (y_train_a[i]==1 and y_train_c[i]==0) else 1 for i in range (0, y_train_a.shape[0])]
		y_test_b = [0 if (y_test_a[i]==1 and y_test_c[i]==0) else 1 for i in range (0, y_test_a.shape[0])]
		np.savetxt(f"y_train_{N}.csv", y_train_b, delimiter=",")
		np.savetxt(f"y_test_{N}.csv", y_test_b, delimiter=",")
		num = X_train_concat_intermediate_output.shape[1]
		y_train_b = to_categorical(y_train_b)
		y_test_b = to_categorical(y_test_b)
		num_classes = y_test_b.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_concat_intermediate_output, y_train_b, validation_data=(X_test_concat_intermediate_output, y_test_b), epochs=100, verbose=2)
		scores = model.evaluate(X_test_concat_intermediate_output, y_test_b, verbose=0)
		print (str (N) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N}.h5")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==4:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		X_train_a, y_train_a = np.loadtxt(f"X_train_{N_a}.csv", delimiter=","), np.loadtxt(f"y_train_{N_a}.csv", delimiter=",")
		X_test_a, y_test_a = np.loadtxt(f"X_test_{N_a}.csv", delimiter=","), np.loadtxt(f"y_test_{N_a}.csv", delimiter=",")
		X_train_c, y_train_c = np.loadtxt(f"X_train_{N_c}.csv", delimiter=","), np.loadtxt(f"y_train_{N_c}.csv", delimiter=",")
		X_test_c, y_test_c = np.loadtxt(f"X_test_{N_c}.csv", delimiter=","), np.loadtxt(f"y_test_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		X_train_a_intermediate_output = intermediate_layer_model_a(X_train_a)
		X_test_a_intermediate_output = intermediate_layer_model_a(X_test_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		X_train_c_intermediate_output = intermediate_layer_model_c(X_train_c)
		X_test_c_intermediate_output = intermediate_layer_model_c(X_test_c)
		X_train_concat_intermediate_output = np.concatenate ((X_train_a_intermediate_output, X_train_c_intermediate_output), axis=1)
		X_test_concat_intermediate_output = np.concatenate ((X_test_a_intermediate_output, X_test_c_intermediate_output), axis=1)
		np.savetxt(f"X_train_{N}.csv", X_train_concat_intermediate_output, delimiter=",")
		np.savetxt(f"X_test_{N}.csv", X_test_concat_intermediate_output, delimiter=",")
		y_train_b = [1 if (y_train_a[i]==y_train_c[i]) else 0 for i in range (0, y_train_a.shape[0])]
		y_test_b = [1 if (y_test_a[i]==y_test_c[i]) else 0 for i in range (0, y_test_a.shape[0])]
		np.savetxt(f"y_train_{N}.csv", y_train_b, delimiter=",")
		np.savetxt(f"y_test_{N}.csv", y_test_b, delimiter=",")
		num = X_train_concat_intermediate_output.shape[1]
		y_train_b = to_categorical(y_train_b)
		y_test_b = to_categorical(y_test_b)
		num_classes = y_test_b.shape[1]
		model = Sequential()
		model.add(Dense(num, activation="relu", input_shape=(num,)))
		model.add(Dense(num_classes, activation="softmax"))
		model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
		model.fit(X_train_concat_intermediate_output, y_train_b, validation_data=(X_test_concat_intermediate_output, y_test_b), epochs=100, verbose=2)
		scores = model.evaluate(X_test_concat_intermediate_output, y_test_b, verbose=0)
		print (str (N) + " ---> " + f"Accuracy: {scores[1]}.")
		model.save(f"{N}.h5")


#total_net(nested_tpls) builds and trains the network corresponding to the full logical propositional reasoning expressed in nested_tpls.

def total_net(nested_tpls):
	for n in range (1, total_number_of_3tpls(nested_tpls)+1):
		nth_stage_neg_0(nested_tpls, n)
		nth_stage_neg_2(nested_tpls, n)
		nth_stage(nested_tpls, n)
		print ("Stage {} of {}: Built and Trained.".format (n, total_number_of_3tpls(nested_tpls)))
	print (f"Building and Training of {nested_tpls}: Completed.")


#nth_stage_neg_0_new_data(new_data, nested_tpls, n) builds the data output, for the new_data, corresponding to the negative at the left in the nth 3-tuple from the list.

def nth_stage_neg_0_new_data(new_data, nested_tpls, n):
	if type (lst_of_all_3tpls(nested_tpls)[n-1][0])!=type (()) and lst_of_all_3tpls(nested_tpls)[n-1][0] < 0:
		N_ = lst_of_all_3tpls(nested_tpls)[n-1][0]
		N = abs (lst_of_all_3tpls(nested_tpls)[n-1][0])
		nd = np.loadtxt(f"{new_data}.csv", delimiter=",")
		pretrained_model = load_model(f"{N}.h5")
		intermediate_layer_model = keras.Model(inputs=pretrained_model.input, outputs=pretrained_model.get_layer("dense_1").output)
		nd_intermediate_output = intermediate_layer_model(nd)
		np.savetxt(f"{new_data}_{N_}.csv", nd_intermediate_output, delimiter=",")


#nth_stage_neg_2_new_data(new_data, nested_tpls, n) builds the data output, for the new_data, corresponding to the negative at the right in the nth 3-tuple from the list.

def nth_stage_neg_2_new_data(new_data, nested_tpls, n):
	if type (lst_of_all_3tpls(nested_tpls)[n-1][2])!=type (()) and lst_of_all_3tpls(nested_tpls)[n-1][2] < 0:
		N_ = lst_of_all_3tpls(nested_tpls)[n-1][2]
		N = abs (lst_of_all_3tpls(nested_tpls)[n-1][2])
		nd = np.loadtxt(f"{new_data}.csv", delimiter=",")
		pretrained_model = load_model(f"{N}.h5")
		intermediate_layer_model = keras.Model(inputs=pretrained_model.input, outputs=pretrained_model.get_layer("dense_1").output)
		nd_intermediate_output = intermediate_layer_model(nd)
		np.savetxt(f"{new_data}_{N_}.csv", nd_intermediate_output, delimiter=",")


#nth_stage_new_data(new_data, nested_tpls, n) builds the data output, for the new_data, corresponding to the nth 3-tuple from the list.

def nth_stage_new_data(new_data, nested_tpls, n):
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==1:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		nd_a = np.loadtxt(f"{new_data}_{N_a}.csv", delimiter=",")
		nd_c = np.loadtxt(f"{new_data}_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		nd_a_intermediate_output = intermediate_layer_model_a(nd_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		nd_c_intermediate_output = intermediate_layer_model_c(nd_c)
		nd_concat_intermediate_output = np.concatenate ((nd_a_intermediate_output, nd_c_intermediate_output), axis=1)
		np.savetxt(f"{new_data}_{N}.csv", nd_concat_intermediate_output, delimiter=",")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==2:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		nd_a = np.loadtxt(f"{new_data}_{N_a}.csv", delimiter=",")
		nd_c = np.loadtxt(f"{new_data}_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		nd_a_intermediate_output = intermediate_layer_model_a(nd_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		nd_c_intermediate_output = intermediate_layer_model_c(nd_c)
		nd_concat_intermediate_output = np.concatenate ((nd_a_intermediate_output, nd_c_intermediate_output), axis=1)
		np.savetxt(f"{new_data}_{N}.csv", nd_concat_intermediate_output, delimiter=",")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==3:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		nd_a = np.loadtxt(f"{new_data}_{N_a}.csv", delimiter=",")
		nd_c = np.loadtxt(f"{new_data}_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		nd_a_intermediate_output = intermediate_layer_model_a(nd_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		nd_c_intermediate_output = intermediate_layer_model_c(nd_c)
		nd_concat_intermediate_output = np.concatenate ((nd_a_intermediate_output, nd_c_intermediate_output), axis=1)
		np.savetxt(f"{new_data}_{N}.csv", nd_concat_intermediate_output, delimiter=",")
	if lst_of_all_3tpls(nested_tpls)[n-1][1]==4:
		N = lst_of_all_3tpls(nested_tpls)[n-1]
		N_a = lst_of_all_3tpls(nested_tpls)[n-1][0]	
		N_c = lst_of_all_3tpls(nested_tpls)[n-1][2]	
		nd_a = np.loadtxt(f"{new_data}_{N_a}.csv", delimiter=",")
		nd_c = np.loadtxt(f"{new_data}_{N_c}.csv", delimiter=",")
		pretrained_model_a = load_model(f"{N_a}.h5")
		pretrained_model_c = load_model(f"{N_c}.h5")
		intermediate_layer_model_a = keras.Model(inputs=pretrained_model_a.input, outputs=pretrained_model_a.get_layer("dense_1").output)
		nd_a_intermediate_output = intermediate_layer_model_a(nd_a)
		intermediate_layer_model_c = keras.Model(inputs=pretrained_model_c.input, outputs=pretrained_model_c.get_layer("dense_1").output)
		nd_c_intermediate_output = intermediate_layer_model_c(nd_c)
		nd_concat_intermediate_output = np.concatenate ((nd_a_intermediate_output, nd_c_intermediate_output), axis=1)
		np.savetxt(f"{new_data}_{N}.csv", nd_concat_intermediate_output, delimiter=",")


#lst_of_all_concepts gives the list of all concepts, in ascending order from innermost to outermost.

def lst_of_all_concepts(nested_tpls):
	lst = []
	for n in range (total_number_of_3tpls(nested_tpls), 0, -1):
		if type (1)==type (nth_innermost_3tpl(nested_tpls, n)[0]):
			lst.append(abs (nth_innermost_3tpl(nested_tpls, n)[0]))
		if type (1)==type (nth_innermost_3tpl(nested_tpls, n)[2]):
			lst.append(abs (nth_innermost_3tpl(nested_tpls, n)[2]))
	return lst


#total_net_new_data(new_data, nested_tpls) builds the data output, for the new_data, corresponding to the full logical propositional reasoning expressed in nested_tpls.

def total_net_new_data(new_data, nested_tpls):
	newd = np.loadtxt(f"{new_data}.csv", delimiter=",")
	for n in range (0, total_number_of_3tpls(nested_tpls)+1):
		np.savetxt(f"{new_data}_{lst_of_all_concepts(nested_tpls)[n]}.csv", newd, delimiter=",")
	for n in range (1, total_number_of_3tpls(nested_tpls)+1):
		nth_stage_neg_0_new_data(new_data, nested_tpls, n)
		nth_stage_neg_2_new_data(new_data, nested_tpls, n)
		nth_stage_new_data(new_data, nested_tpls, n)
	pretrained_model = load_model(f"{nested_tpls}.h5")
	ndata = np.loadtxt(f"{new_data}_{nested_tpls}.csv", delimiter=",")
	predictions = pretrained_model.predict(ndata)
	return predictions


#the reasoning class summarizes it all: a reasoning has as attribute its nested_tpls, the methods are the programming of this reasoning
#and the forming of predictions from new data.

class reasoning:
    def __init__(self, nested_tpls):
        self.nested_tpls = nested_tpls
    def programme(self):
        return total_net(self.nested_tpls)
    def ndpredict(self, new_data):
        return total_net_new_data(new_data, self.nested_tpls)

#-------------------------------------------------------------------------------------------------------------------------------