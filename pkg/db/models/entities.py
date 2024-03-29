from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Identity, Integer, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import declarative_base, relationship

from pkg.db.db import db


class Item(db.Model):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    price = Column(Float(precision=2), nullable=False)

    def __repr__(self):
        return 'ItemModel(id=%d,name=%s, price=%s,)' % (self.id, self.name, self.price)

    def json(self):
        return {'id': self.id, 'name': self.name, 'price': self.price}


### Generated by sqlacodegen
Base = declarative_base()
metadata = Base.metadata


class AspNetRoles(Base):
    __tablename__ = 'AspNetRoles'

    Id = Column(Text, primary_key=True)
    Name = Column(String(256))
    NormalizedName = Column(String(256), unique=True)
    ConcurrencyStamp = Column(Text)

    AspNetUsers = relationship('AspNetUsers', secondary='AspNetUserRoles', back_populates='AspNetRoles')
    AspNetRoleClaims = relationship('AspNetRoleClaims', back_populates='AspNetRoles')
    UserOfferings = relationship('UserOfferings', back_populates='AspNetRoles')


class Dictionaries(Base):
    __tablename__ = 'Dictionaries'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Key = Column(Text)
    Value = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)


class FileRecords(Base):
    __tablename__ = 'FileRecords'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    PrivatePath = Column(Text)
    Hash = Column(Text)
    FileName = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Images = relationship('Images', back_populates='FileRecords')
    Videos = relationship('Videos', foreign_keys='[Videos.AudioId]', back_populates='FileRecords')
    Videos_ = relationship('Videos', foreign_keys='[Videos.ProcessedVideo1Id]', back_populates='FileRecords_')
    Videos1 = relationship('Videos', foreign_keys='[Videos.ProcessedVideo2Id]', back_populates='FileRecords1')
    Videos2 = relationship('Videos', foreign_keys='[Videos.Video1Id]', back_populates='FileRecords2')
    Videos3 = relationship('Videos', foreign_keys='[Videos.Video2Id]', back_populates='FileRecords3')
    Transcriptions = relationship('Transcriptions', foreign_keys='[Transcriptions.FileId]', back_populates='FileRecords')
    Transcriptions_ = relationship('Transcriptions', foreign_keys='[Transcriptions.SrtFileId]', back_populates='FileRecords_')


class Logs(Base):
    __tablename__ = 'Logs'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    Json = Column(Text, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    UserId = Column(Text)
    OfferingId = Column(Text)
    MediaId = Column(Text)
    EventType = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)


class TaskItems(Base):
    __tablename__ = 'TaskItems'
    __table_args__ = (
        UniqueConstraint('UniqueId', 'TaskType'),
    )

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    UniqueId = Column(Text, nullable=False)
    TaskType = Column(Integer, nullable=False)
    TaskParameters = Column(Text, nullable=False)
    ResultData = Column(Text, nullable=False)
    AttemptNumber = Column(Integer, nullable=False, server_default=text('0'))
    MediaId = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    OfferingId = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    OpaqueMessageRef = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    PercentComplete = Column(Integer, nullable=False, server_default=text('0'))
    PlaylistId = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    RemoteResultData = Column(Text, nullable=False)
    Rule = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    TaskStatusCode = Column(Integer, nullable=False, server_default=text('0'))
    UserId = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    VideoId = Column(Text, nullable=False, unique=True, server_default=text("''::text"))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    AncestorTaskItemId = Column(Text)
    DebugMessage = Column(Text)
    EndedAt = Column(DateTime)
    EstimatedCompletionAt = Column(DateTime)
    ParentTaskItemId = Column(Text)
    PreviousAttemptTaskItemId = Column(Text)
    QueuedAt = Column(DateTime)
    StartedAt = Column(DateTime)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)


class Universities(Base):
    __tablename__ = 'Universities'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Name = Column(Text)
    Domain = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='Universities')
    Departments = relationship('Departments', back_populates='Universities')
    Terms = relationship('Terms', back_populates='Universities')


class EFMigrationsHistory(Base):
    __tablename__ = '__EFMigrationsHistory'

    MigrationId = Column(String(150), primary_key=True)
    ProductVersion = Column(String(32), nullable=False)


class AspNetRoleClaims(Base):
    __tablename__ = 'AspNetRoleClaims'

    Id = Column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    RoleId = Column(ForeignKey('AspNetRoles.Id', ondelete='CASCADE'), nullable=False, index=True)
    ClaimType = Column(Text)
    ClaimValue = Column(Text)

    AspNetRoles = relationship('AspNetRoles', back_populates='AspNetRoleClaims')


class AspNetUsers(Base):
    __tablename__ = 'AspNetUsers'

    Id = Column(Text, primary_key=True)
    EmailConfirmed = Column(Boolean, nullable=False)
    PhoneNumberConfirmed = Column(Boolean, nullable=False)
    TwoFactorEnabled = Column(Boolean, nullable=False)
    LockoutEnabled = Column(Boolean, nullable=False)
    AccessFailedCount = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False, server_default=text('0'))
    Metadata = Column(Text, nullable=False)
    UserName = Column(String(256))
    NormalizedUserName = Column(String(256), unique=True)
    Email = Column(String(256))
    NormalizedEmail = Column(String(256), index=True)
    PasswordHash = Column(Text)
    SecurityStamp = Column(Text)
    ConcurrencyStamp = Column(Text)
    PhoneNumber = Column(Text)
    LockoutEnd = Column(DateTime(True))
    FirstName = Column(Text)
    LastName = Column(Text)
    UniversityId = Column(ForeignKey('Universities.Id', ondelete='RESTRICT'), index=True)

    AspNetRoles = relationship('AspNetRoles', secondary='AspNetUserRoles', back_populates='AspNetUsers')
    Universities = relationship('Universities', back_populates='AspNetUsers')
    AspNetUserClaims = relationship('AspNetUserClaims', back_populates='AspNetUsers')
    AspNetUserLogins = relationship('AspNetUserLogins', back_populates='AspNetUsers')
    AspNetUserTokens = relationship('AspNetUserTokens', back_populates='AspNetUsers')
    Messages = relationship('Messages', back_populates='AspNetUsers')
    Subscriptions = relationship('Subscriptions', back_populates='AspNetUsers')
    UserOfferings = relationship('UserOfferings', back_populates='AspNetUsers')
    WatchHistories = relationship('WatchHistories', back_populates='AspNetUsers')


class Departments(Base):
    __tablename__ = 'Departments'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Name = Column(Text)
    Acronym = Column(Text)
    UniversityId = Column(ForeignKey('Universities.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Universities = relationship('Universities', back_populates='Departments')
    Courses = relationship('Courses', back_populates='Departments')


class Images(Base):
    __tablename__ = 'Images'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    SourceType = Column(Integer, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    SourceId = Column(Text)
    ImageFileId = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    FileRecords = relationship('FileRecords', back_populates='Images')


class Terms(Base):
    __tablename__ = 'Terms'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime, nullable=False, server_default=text("'0001-01-01 00:00:00'::timestamp without time zone"))
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Name = Column(Text)
    UniversityId = Column(ForeignKey('Universities.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Universities = relationship('Universities', back_populates='Terms')
    Offerings = relationship('Offerings', back_populates='Terms')


class Videos(Base):
    __tablename__ = 'Videos'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    TranscribingAttempts = Column(Integer, nullable=False, server_default=text('0'))
    JsonMetadata = Column(Text, nullable=False)
    SceneData = Column(Text, nullable=False)
    FileMediaInfo = Column(Text, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    AudioId = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    Description = Column(Text)
    Video1Id = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    Video2Id = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    TranscriptionStatus = Column(Text)
    ProcessedVideo1Id = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    ProcessedVideo2Id = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    Duration = Column(INTERVAL)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)
    PhraseHints = Column(Text)

    FileRecords = relationship('FileRecords', foreign_keys='[Videos.AudioId]', back_populates='Videos')
    FileRecords_ = relationship('FileRecords', foreign_keys='[Videos.ProcessedVideo1Id]', back_populates='Videos_')
    FileRecords1 = relationship('FileRecords', foreign_keys='[Videos.ProcessedVideo2Id]', back_populates='Videos1')
    FileRecords2 = relationship('FileRecords', foreign_keys='[Videos.Video1Id]', back_populates='Videos2')
    FileRecords3 = relationship('FileRecords', foreign_keys='[Videos.Video2Id]', back_populates='Videos3')
    EPubs = relationship('EPubs', back_populates='Videos')
    Transcriptions = relationship('Transcriptions', back_populates='Videos')
    Medias = relationship('Medias', back_populates='Videos')


class AspNetUserClaims(Base):
    __tablename__ = 'AspNetUserClaims'

    Id = Column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    UserId = Column(ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), nullable=False, index=True)
    ClaimType = Column(Text)
    ClaimValue = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='AspNetUserClaims')


class AspNetUserLogins(Base):
    __tablename__ = 'AspNetUserLogins'

    LoginProvider = Column(Text, primary_key=True, nullable=False)
    ProviderKey = Column(Text, primary_key=True, nullable=False)
    UserId = Column(ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), nullable=False, index=True)
    ProviderDisplayName = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='AspNetUserLogins')


t_AspNetUserRoles = Table(
    'AspNetUserRoles', metadata,
    Column('UserId', ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('RoleId', ForeignKey('AspNetRoles.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class AspNetUserTokens(Base):
    __tablename__ = 'AspNetUserTokens'

    UserId = Column(ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), primary_key=True, nullable=False)
    LoginProvider = Column(Text, primary_key=True, nullable=False)
    Name = Column(Text, primary_key=True, nullable=False)
    Value = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='AspNetUserTokens')


class Courses(Base):
    __tablename__ = 'Courses'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    CourseNumber = Column(Text)
    DepartmentId = Column(ForeignKey('Departments.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)
    FilePath = Column(Text)

    Departments = relationship('Departments', back_populates='Courses')
    CourseOfferings = relationship('CourseOfferings', back_populates='Courses')


class EPubs(Base):
    __tablename__ = 'EPubs'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    Cover = Column(Text, nullable=False)
    SourceType = Column(Integer, nullable=False, server_default=text('0'))
    PublishStatus = Column(Integer, nullable=False, server_default=text('0'))
    Visibility = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Language = Column(Text)
    VideoId = Column(ForeignKey('Videos.Id', ondelete='RESTRICT'), index=True)
    Author = Column(Text)
    Chapters = Column(Text)
    Filename = Column(Text)
    Publisher = Column(Text)
    SourceId = Column(Text)
    Title = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Videos = relationship('Videos', back_populates='EPubs')


class Messages(Base):
    __tablename__ = 'Messages'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    Payload = Column(Text, nullable=False)
    LogLevel = Column(Integer, nullable=False)
    Ack = Column(Integer, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    ApplicationUserId = Column(ForeignKey('AspNetUsers.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='Messages')


class Offerings(Base):
    __tablename__ = 'Offerings'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    AccessType = Column(Integer, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    LogEventsFlag = Column(Boolean, nullable=False, server_default=text('false'))
    JsonMetadata = Column(Text, nullable=False)
    Visibility = Column(Integer, nullable=False, server_default=text('0'))
    PublishStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    SectionName = Column(Text)
    TermId = Column(ForeignKey('Terms.Id', ondelete='RESTRICT'), index=True)
    CourseName = Column(Text)
    Description = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Terms = relationship('Terms', back_populates='Offerings')
    CourseOfferings = relationship('CourseOfferings', back_populates='Offerings')
    Playlists = relationship('Playlists', back_populates='Offerings')
    UserOfferings = relationship('UserOfferings', back_populates='Offerings')


class Subscriptions(Base):
    __tablename__ = 'Subscriptions'
    __table_args__ = (
        UniqueConstraint('ResourceType', 'ResourceId', 'ApplicationUserId'),
    )

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    ResourceType = Column(Integer, nullable=False)
    ResourceId = Column(Text, nullable=False)
    ApplicationUserId = Column(ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), nullable=False, index=True)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='Subscriptions')


class Transcriptions(Base):
    __tablename__ = 'Transcriptions'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    Editable = Column(Integer, nullable=False, server_default=text('0'))
    PublishStatus = Column(Integer, nullable=False, server_default=text('0'))
    TranscriptionType = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    FileId = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    Description = Column(Text)
    Language = Column(Text)
    VideoId = Column(ForeignKey('Videos.Id', ondelete='RESTRICT'), index=True)
    SrtFileId = Column(ForeignKey('FileRecords.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)
    Label = Column(Text)
    SourceInternalRef = Column(Text)
    SourceLabel = Column(Text)

    FileRecords = relationship('FileRecords', foreign_keys=[FileId], back_populates='Transcriptions')
    FileRecords_ = relationship('FileRecords', foreign_keys=[SrtFileId], back_populates='Transcriptions_')
    Videos = relationship('Videos', back_populates='Transcriptions')
    Captions = relationship('Captions', back_populates='Transcriptions')


class Captions(Base):
    __tablename__ = 'Captions'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    Begin = Column(INTERVAL, nullable=False)
    End = Column(INTERVAL, nullable=False)
    Index = Column(Integer, nullable=False, server_default=text('0'))
    DownVote = Column(Integer, nullable=False, server_default=text('0'))
    UpVote = Column(Integer, nullable=False, server_default=text('0'))
    CaptionType = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    Text_ = Column('Text', Text)
    TranscriptionId = Column(ForeignKey('Transcriptions.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Transcriptions = relationship('Transcriptions', back_populates='Captions')


class CourseOfferings(Base):
    __tablename__ = 'CourseOfferings'

    CourseId = Column(ForeignKey('Courses.Id', ondelete='CASCADE'), primary_key=True, nullable=False)
    OfferingId = Column(ForeignKey('Offerings.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    Id = Column(Text)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)
    FilePath = Column(Text)

    Courses = relationship('Courses', back_populates='CourseOfferings')
    Offerings = relationship('Offerings', back_populates='CourseOfferings')


class Playlists(Base):
    __tablename__ = 'Playlists'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    SourceType = Column(Integer, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    JsonMetadata = Column(Text, nullable=False)
    Index = Column(Integer, nullable=False, server_default=text('0'))
    Visibility = Column(Integer, nullable=False, server_default=text('0'))
    PublishStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    PlaylistIdentifier = Column(Text)
    Name = Column(Text)
    OfferingId = Column(ForeignKey('Offerings.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Offerings = relationship('Offerings', back_populates='Playlists')
    Medias = relationship('Medias', back_populates='Playlists')


class UserOfferings(Base):
    __tablename__ = 'UserOfferings'

    OfferingId = Column(ForeignKey('Offerings.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    ApplicationUserId = Column(ForeignKey('AspNetUsers.Id', ondelete='CASCADE'), primary_key=True, nullable=False)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IdentityRoleId = Column(ForeignKey('AspNetRoles.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    Id = Column(Text)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='UserOfferings')
    AspNetRoles = relationship('AspNetRoles', back_populates='UserOfferings')
    Offerings = relationship('Offerings', back_populates='UserOfferings')


class Medias(Base):
    __tablename__ = 'Medias'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    JsonMetadata = Column(Text, nullable=False)
    SourceType = Column(Integer, nullable=False, server_default=text('0'))
    IsDeletedStatus = Column(Integer, nullable=False, server_default=text('0'))
    Index = Column(Integer, nullable=False, server_default=text('0'))
    Visibility = Column(Integer, nullable=False, server_default=text('0'))
    PublishStatus = Column(Integer, nullable=False, server_default=text('0'))
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    UniqueMediaIdentifier = Column(Text)
    PlaylistId = Column(ForeignKey('Playlists.Id', ondelete='RESTRICT'), index=True)
    VideoId = Column(ForeignKey('Videos.Id', ondelete='RESTRICT'), index=True)
    Name = Column(Text)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    Playlists = relationship('Playlists', back_populates='Medias')
    Videos = relationship('Videos', back_populates='Medias')
    WatchHistories = relationship('WatchHistories', back_populates='Medias')


class WatchHistories(Base):
    __tablename__ = 'WatchHistories'

    Id = Column(Text, primary_key=True)
    CreatedAt = Column(DateTime, nullable=False)
    LastUpdatedAt = Column(DateTime, nullable=False)
    IsDeletedStatus = Column(Integer, nullable=False)
    Json = Column(Text, nullable=False)
    CreatedBy = Column(Text)
    LastUpdatedBy = Column(Text)
    MediaId = Column(ForeignKey('Medias.Id', ondelete='RESTRICT'), index=True)
    ApplicationUserId = Column(ForeignKey('AspNetUsers.Id', ondelete='RESTRICT'), index=True)
    DeletedAt = Column(DateTime)
    DeletedBy = Column(Text)

    AspNetUsers = relationship('AspNetUsers', back_populates='WatchHistories')
    Medias = relationship('Medias', back_populates='WatchHistories')
