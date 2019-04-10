from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, User, Category, Item

# Create new db session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

print("Session successfully created!")


# Create a test user
user1 = User(id=7,
             name="John Snow",
             email="youknownothing@johnsnow.com",
             picture='https://pbs.twimg.com/profile_images/901947348699545601/hqRMHITj_400x400.jpg')

session.add(user1)
session.commit()


'''
#### Football ####
'''


football = Category(name="Football")

session.add(football)
session.commit()

football_cleats = Item(name="Nike Vapor Untouchable 3 Cleats",
                       description="The most dynamic players on the gridiron deserve the breathable fit and explosive responsiveness of the Untouchable Pro.",
                       user_id="7",
                       category=football)

session.add(football_cleats)
session.commit()

football_gloves = Item(name="Nike Vapor Jet 5.0 Football Gloves",
                       description="The most famous glove in football: The Nike Vapor Jet. Now in it's fifth version, an updated design provides skill players with not just unmatched catching ability but also streamlined protection. As the game gets more physical, so does the Vapor Jet.",
                       user_id="7",
                       category=football)

session.add(football_gloves)
session.commit()

football_helmet = Item(name="Ridell Revolution Speed Football Helmet",
                       description="An ABS gloss shell combines with moisture-wicking liner for protection against high-impact hits. Inflatable S-pads and oversized vent holes deliver a comfortable feel. Your little one can jump the snap this year with the Riddell Revolution Speed Youth Football Helmet.",
                       user_id="7",
                       category=football)

session.add(football_helmet)
session.commit()

'''
#### Basketball ####
'''


basketball = Category(name="Basketball")

session.add(basketball)
session.commit()

basketball_shoes = Item(name="UA Curry 6 Basketball Shoe",
                        description="Fully knit upper for a breathable, compression-like fit that delivers lightweight directional strength",
                        user_id="7",
                        category=basketball)

session.add(basketball_shoes)
session.commit()

basketball_shorts = Item(name="Nike Dry Elite Basketball Shorts",
                         description="A personalized fit and moisture-wicking technology team up in the Nike Dry Elite Stripe Basketball Shorts. Dri-Fit technology provides moisture-wicking comfort so you can maximize performance with ease. Complete with multiple pockets for storage, this Nike style delivers during any activity.",
                         user_id="7",
                         category=basketball)

session.add(basketball_shorts)
session.commit()

shooting_sleeve = Item(name="Nike NBA Shooting Sleeve",
                       description="The official on-court sleeve of the NBA, the Nike NBA Shooter Sleeve provides the compression benefits and DRI-Fit technology that elite athletes crave when stepping onto the floor.",
                       user_id="7",
                       category=basketball)

session.add(shooting_sleeve)
session.commit()

'''
#### Boxing ####
'''


boxing = Category(name="Boxing")

session.add(boxing)
session.commit()

boxing_shoes = Item(name="Title Predator Boxing Shoes",
                    description="Stick and move with the best of them in the Predator boxing shoes. A three dimensional upper molds to the shape of your feet while also providing optimal fit of your ankle and lower calf. The flexibility of the upper keeps your foot supported and won't thin out or become vulnerable over time. The Title Predator boxing shoe has a flexibile gum rubber outsole that delivers maximum traction and speed for enhanced performance in the ring.",
                    user_id="7",
                    category=boxing)

session.add(boxing_shoes)
session.commit()

boxing_gloves = Item(name="Everlast Powerlock Training Gloves",
                     description="Designed with Powerlock Technology, the Everlast Powerlock Training Gloves feature an ergonomic layered construction that puts your hand into a natural fist position.",
                     user_id="7",
                     category=boxing)

session.add(boxing_gloves)
session.commit()

punching_bag = Item(name="Ringside 70 lb. Leather Heavy Bag",
                    description="Throw everything you've got and more at the Ringside Leather Heavy Bag. The bag comes filled and weighs approximately 70 lbs. A heavy bag chain and swivel are included for easy mounting. Train like a champion with the Ringside Leather Heavy Bag.",
                    user_id="7",
                    category=boxing)

session.add(punching_bag)
session.commit()


'''
#### Track & Field ####
'''


track = Category(name="Track & Field")

session.add(track)
session.commit()

running_shoes = Item(name="Nike Free Flyknit Running Shoes",
                     description="Made for short runs when you want a barefoot-like feel, the Nike Free RN Flyknit is the lightest in the Free RN family. Its sock-lick upper has more stretch yarns than previous versions, so it hugs your feet more than ever. The innovative sole has an updated construction, yet still expands and contracts with every movement. The packable design makes the shoe easy to stuff into your bag-so youcan get in a few miles on the fly.",
                     user_id="7",
                     category=track)

session.add(running_shoes)
session.commit()

track_spikes = Item(name="Adidas Adizero Prime Track Spikes",
                    description="If less is more, these spikes are the pinnacle of speed and simplicity. The track and field shoes feature a SPRINTWEB seamless upper with a laminate composite that locks the foot down during high-level acceleration while maintaining a barefoot feel",
                    user_id="7",
                    category=track)

session.add(track_spikes)
session.commit()

print('We created the test data!')
