import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from build import build_model
import numpy as np
from sklearn.utils import class_weight
from sklearn.metrics import precision_score, recall_score, accuracy_score

def train_model():
    train_dir = 'dataset/train'
    validation_dir = 'dataset/validation'

    train_datagen = ImageDataGenerator(
        rescale=1.0/255.0,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    validation_datagen = ImageDataGenerator(rescale=1.0/255.0)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=20,
        class_mode='binary'
    )

    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=(150, 150),
        batch_size=20,
        class_mode='binary'
    )

    model = build_model()

    # Compute class weights
    class_weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    class_weights = {i: class_weights[i] for i in range(len(class_weights))}
    
    history = model.fit(
        train_generator,
        steps_per_epoch=100,
        epochs=50,
        validation_data=validation_generator,
        validation_steps=50
    )

    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(len(acc))

    plt.plot(epochs, acc, 'r', label='Training accuracy')
    plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
    plt.title('Training and validation accuracy')
    plt.legend()
    plt.figure()

    plt.plot(epochs, loss, 'r', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()
    plt.show()

    model.save('fake_logo_detector (2).h5')

    y_true = validation_generator.classes


    y_pred_probs = model.predict(validation_generator, steps=len(y_true))

    y_pred = (y_pred_probs > 0.5).astype("int32")

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)
    error_rate = 1 - accuracy
    avg_confidence = np.mean(np.where(y_pred == y_true, y_pred_probs, 1 - y_pred_probs))

    print("\n📊 Final Validation Metrics:")
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"📉 Error Rate: {error_rate:.4f}")
    print(f"🎯 Precision: {precision:.4f}")
    print(f"🔁 Recall: {recall:.4f}")
    print(f"💡 Average Confidence: {avg_confidence:.4f}")
#

if __name__ == "__main__":
    train_model()
#
